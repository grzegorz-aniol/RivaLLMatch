import concurrent.futures
import sqlite3
import time
from typing import Dict

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from contests.competition_template import CompetitionTemplate
from entities.duel_result import DuelResult
from job_queue import DuelsQueue
from logger import Logger
from messages.duel_request_message import DuelRequestMessage
from models import get_model_name
from score import parse_score, CompetitionScores
from storage import Storage
from utils import now, wrap


class RetryRequestException(Exception):
    pass


class ResumableArena:
    logger = Logger()

    def __init__(self, storage: Storage, duels_queue: DuelsQueue, competition_template: CompetitionTemplate, llms):
        self.storage = storage
        self.duels_queue = duels_queue
        self.llms = list(llms)
        self.competition_template = competition_template
        self.template_id = competition_template.get_template_id()
        self.metric_keys = competition_template.get_metric_keys()
        self.model_names = [get_model_name(llm) for llm in self.llms]
        self.model_name_to_index = {get_model_name(llm): n for n, llm in enumerate(self.llms)}
        self.model_name_to_obj = {get_model_name(llm): llm for llm in self.llms}
        self.competition_scores = CompetitionScores(len(llms), self.metric_keys)

    def run(self, n_jobs=1) -> CompetitionScores:
        start_time = now()

        self.run_duels(n_jobs, start_time)
        self.generate_results()

        total_time = now() - start_time

        self.logger.info(f'Done. Total time: {total_time:.1f} sec')
        self.show_results()
        return self.competition_scores

    def run_duels(self, n_jobs, start_time):
        self.logger.info('Starting duels')
        try:
            self.duels_queue.queue.prune(include_failed=False)
        except sqlite3.OperationalError:
            pass
        self.duels_queue.retry_failed()
        self.duels_queue.retry_locked()
        futures = []
        last_update_ts = 0.0
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_jobs) as executor:
            all_processed = False
            while not all_processed:
                if time.time() - last_update_ts > 5.0:
                    last_update_ts = time.time()
                    n_duels_to_done = self.duels_queue.queue.qsize()
                    self.logger.info(f'Number of pending duels in the queue: {n_duels_to_done}')
                message = self.duels_queue.get()
                all_processed = (message is None)
                if message:
                    feature = executor.submit(lambda arg: self.__dispatch_duel(arg), message)
                    futures.append(feature)
        self.logger.info('Waiting for results...')
        concurrent.futures.wait(futures)
        self.duels_queue.prune(include_failed=False)
        self.logger.info(f'Done. Time: {now() - start_time:.1f} sec')
        executor.shutdown()

    def generate_results(self):
        for duel_result in self.storage.get_all_results():
            master_index = self.model_name_to_index[duel_result.master_model]
            student_index = self.model_name_to_index[duel_result.student_model]
            self.competition_scores.update(master_index, student_index, duel_result.scores_json)
        self.competition_scores.dump(f'./workdir/{self.template_id}_scores.pkl')

    def __dispatch_duel(self, message: DuelRequestMessage):
        try:
            student = self.model_name_to_obj[message.student_model]
            master = self.model_name_to_obj[message.master_model]
            task = message.task
            answer = self.invoke_chat('Answer', chat=student,
                                      template=self.competition_template.get_question_template(),
                                      var_dict={'task': task}, log_result=True)
            scores_json = self.invoke_chat('Scores', chat=master,
                                           template=self.competition_template.get_answer_evaluation(),
                                           var_dict={'task': task, 'answer': answer}, log_result=True)
            scores = parse_score(scores_json)

            self.logger.info(f'Duel between {get_model_name(master)} (master) '
                             f'and {get_model_name(student)} (student)\n    -> student scores: {scores}')

            duel_result = DuelResult()
            duel_result.created_ts = time.time_ns() // 1_000
            duel_result.master_model = get_model_name(master)
            duel_result.student_model = get_model_name(student)
            duel_result.scores_json = scores
            self.storage.save_duel_result(duel_result)
            self.duels_queue.mark_done(message)

        except BaseException as ex:
            self.logger.error(f'Error: {ex}')
            self.duels_queue.mark_failed(message)
            return None

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
    def __score_to_str(score: Dict[str, float]) -> str:
        return ','.join([f'{key}={value:.3f}' for key, value in score.items()])

    @staticmethod
    def invoke_chat(name, chat, template, var_dict=None, log_result=True):
        if var_dict is None:
            var_dict = {}
        task_selection_chain = template | chat
        st = now()
        response = ResumableArena.__invoke_with_retry(task_selection_chain, var_dict)
        response_time = now() - st
        result = response.content
        if log_result:
            ResumableArena.logger.debug(f'{name}:\n{wrap(result)}\nTime: {response_time:.1f} sec')
        return result

    @staticmethod
    @retry(stop=stop_after_attempt(20), wait=wait_exponential(min=1, max=32),
           retry=retry_if_exception_type(RetryRequestException))
    def __invoke_with_retry(chain, dicts):
        try:
            response = chain.invoke(dicts)
            return response
        except BaseException as ex:
            message = str(ex)
            if ('Error code: 429' in message) or ('rate_limit_error' in message):
                Logger.debug(f'Rate limit error: {message}')
                raise RetryRequestException()
            if 'Error code: 503' in message:
                Logger.debug(f'Service unavailable: {message}')
                raise RetryRequestException()
            Logger.error(message)
