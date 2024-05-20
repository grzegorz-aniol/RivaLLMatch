import concurrent.futures

from itertools import permutations
from logger import Logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from contests.competition_templates import CompetitionTemplates
from models import get_model_name
from score import parse_score, Score, CompetitionScores
from utils import now, wrap


class RateLimitException(Exception):
    pass


class Arena:
    logger = Logger()

    def __init__(self, competition_templates: CompetitionTemplates, llms, n_jobs=1):
        self.llms = list(llms)
        self.competition_templates = competition_templates
        self.model_names = [get_model_name(llm) for llm in self.llms]
        self.model_name_to_index = {get_model_name(llm): n for n, llm in enumerate(self.llms)}
        self.competition_scores = CompetitionScores(len(llms))
        self.n_jobs = n_jobs
        self.sync_models = {'mixtral-8x7b-32768'}

    def run(self, n_rounds=1):
        n_llms = len(self.llms)
        if n_llms < 2:
            raise Exception('Too small number of LLMs. At least two should be provided to start a competition.')
        pairs = list(permutations(self.llms, 2))

        self.logger.info(f'Starting competition: {self.competition_templates.get_templates_set_name()}')
        self.logger.info(f'Number of rounds: {n_rounds}')
        self.logger.info(f'Number of clashes: {n_rounds * len(pairs)}')
        self.logger.info(f'Models under evaluation: {self.model_names}')
        self.logger.info('')

        start_time = now()

        tasks = self.__build_tasks(n_rounds)

        self.logger.info('Starting competition rounds')

        for n in range(n_rounds):
            self.logger.info('-------------------------------------------------------------------------------')
            self.logger.info(f'Round: {n + 1}')
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.n_jobs) as executor:
                task_index = n
                futures = []
                round_start_time = now()
                self.logger.info('Scheduling calls...')
                for master, student in pairs:
                    task = tasks[task_index]
                    feature = executor.submit(lambda args: self.__dispatch_clash(*args),
                                              (task, student, master, self.competition_templates))
                    futures.append(feature)
                    # wait for some models with low TPM limits
                    # if self.__sync_call(master, student):
                    #     concurrent.futures.wait([feature])
                self.logger.info('Waiting for results...')
                concurrent.futures.wait(futures)
                self.logger.info(f'Round done. Time: {now()-round_start_time:.1f} sec')
                executor.shutdown()

        total_time = now() - start_time

        self.logger.info(f'Done. Total time: {total_time:.1f} sec')
        self.show_results()
        return self.competition_scores

    def __dispatch_clash(self, task, student, master, template):
        try:
            answer = self.invoke_chat('Answer', chat=student,
                                      template=template.get_question_template(),
                                      var_dict={'task': task}, log_result=False)
            scores_json = self.invoke_chat('Scores', chat=master,
                                           template=template.get_answer_evaluation(),
                                           var_dict={'task': task, 'answer': answer}, log_result=False)
            scores = parse_score(scores_json)
            master_index = self.model_name_to_index[get_model_name(master)]
            student_index = self.model_name_to_index[get_model_name(student)]
            self.logger.info(f'Clash between {get_model_name(master)} (master) '
                             f'and {get_model_name(student)} (student)\n    -> student scores: {scores}')
            self.competition_scores.update(master_index, student_index, scores)
            return scores
        except BaseException as ex:
            self.logger.error(ex)
            return None

    def __sync_call(self, master, student):
        if get_model_name(student) in self.sync_models or get_model_name(master) in self.sync_models:
            return True
        return False

    def show_results(self):
        n_llms = len(self.llms)
        self.logger.info('Final results:')
        self.logger.info(' > student scores (received):')
        student_avg_scores = self.competition_scores.get_student_avg_score()
        for n in range(n_llms):
            llm = self.llms[n]
            model_name = get_model_name(llm)
            avg_scores = student_avg_scores[n]
            if avg_scores:
                self.logger.info(f"   > Model: {model_name} average scores: {self.__score_to_str(avg_scores)}")
            else:
                self.logger.info(f"Model: {model_name} - no score")
        self.logger.info(' > master scores (given):')
        master_avg_scores = self.competition_scores.get_master_avg_score()
        for n in range(n_llms):
            llm = self.llms[n]
            model_name = get_model_name(llm)
            avg_scores = master_avg_scores[n]
            if avg_scores:
                self.logger.info(f"   > Model: {model_name} average scores: {self.__score_to_str(avg_scores)}")
            else:
                self.logger.info(f"Model: {model_name} - no score")

    @staticmethod
    def __score_to_str(score: Score) -> str:
        return (f"accuracy={score.accuracy:.3f}, "
                f"clarity={score.clarity:.3f}, "
                f"depth={score.depth:.3f}, "
                f"reasoning={score.reasoning:.3f}")

    def __build_tasks(self, n_tasks):
        self.logger.info('Generate list of tasks')
        n_llms = len(self.llms)
        tasks = []
        for n in range(n_tasks):
            model_index = n % n_llms
            llm = self.llms[model_index]
            self.logger.info(f'Querying model: {self.model_names[model_index]}')
            task = self.invoke_chat(f'Task #{n + 1}', chat=llm,
                                    template=self.competition_templates.get_task_selection_template())
            tasks.append(task)
        self.logger.info('Done')
        return tasks

    @staticmethod
    def invoke_chat(name, chat, template, var_dict=None, log_result=True):
        if var_dict is None:
            var_dict = {}
        task_selection_chain = template | chat
        st = now()
        response = Arena.__invoke_with_retry(task_selection_chain, var_dict)
        time = now() - st
        result = response.content
        if log_result:
            Arena.logger.debug(f'{name}: {wrap(result)}\nTime: {time:.1f} sec')
        return result

    @staticmethod
    @retry(stop=stop_after_attempt(20), wait=wait_exponential(min=1, max=32),
           retry=retry_if_exception_type(RateLimitException))
    def __invoke_with_retry(chain, dicts):
        try:
            response = chain.invoke(dicts)
            return response
        except BaseException as ex:
            message = str(ex)
            if 'Error code: 429' in message:
                Logger.debug(f'Rate limit error: {message}')
                raise RateLimitException()
            if 'rate_limit_error' in message:
                Logger.debug(f'Rate limit error: {message}')
                raise RateLimitException()
