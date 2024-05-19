import random
from itertools import permutations
from logger import Logger

from contests.problem_templates import ProblemTemplates
from models import get_model_name
from score import parse_score, Score, CompetitionScores
from utils import now, wrap



class Arena:
    logger = Logger()

    def __init__(self, problem_templates: ProblemTemplates, llms):
        self.llms = list(llms)
        self.problem_templates = problem_templates
        self.model_names = [get_model_name(llm) for llm in self.llms]
        self.model_name_to_index = {get_model_name(llm): n for n, llm in enumerate(self.llms)}
        self.competition_scores = CompetitionScores(len(llms))

    def run(self, n_rounds=1):
        n_llms = len(self.llms)
        if n_llms < 2:
            raise Exception('Too small number of LLMs. At least two should be provided to start a competition.')
        pairs = list(permutations(self.llms, 2))

        self.logger.info(f'Starting competition: {self.problem_templates.get_templates_set_name()}')
        self.logger.info(f'Number of rounds: {n_rounds}')
        self.logger.info(f'Number of clashes: {n_rounds * len(pairs)}')
        self.logger.info(f'Models under evaluation: {self.model_names}')
        self.logger.info('')

        start_time = now()

        problems = self.__build_problems(n_rounds)

        self.logger.info('Starting competition rounds')
        for n in range(n_rounds):
            self.logger.info('-------------------------------------------------------------------------------')
            self.logger.info(f'Round: {n + 1}')
            problem_index = n
            for master, student in pairs:
                master_index = self.model_name_to_index[get_model_name(master)]
                student_index = self.model_name_to_index[get_model_name(student)]
                problem = problems[problem_index]
                self.logger.info(f'Clash between {get_model_name(master)} (master) '
                                 f'and {get_model_name(student)} (student)')

                try:
                    answer = self.invoke_chat('Answer', chat=student,
                                              template=self.problem_templates.get_question_template(),
                                              var_dict={'problem': problem})

                    scores_json = self.invoke_chat('Scores', chat=master,
                                                   template=self.problem_templates.get_answer_evaluation(),
                                                   var_dict={'problem': problem, 'answer': answer}, log_result=False)
                    scores = parse_score(clean_json_result(scores_json))
                    self.logger.info(f'Student scores: {scores}')
                    self.competition_scores.update(master_index, student_index, scores)
                except BaseException as ex:
                    self.logger.error(ex)

        total_time = now() - start_time
        self.logger.info(f'Done. Total time: {total_time:.0f} sec')
        self.show_results()
        return self.competition_scores

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

    def __build_problems(self, n_problems):
        self.logger.info('Generate list of problems')
        n_llms = len(self.llms)
        problems = []
        for n in range(n_problems):
            model_index = n % n_llms
            llm = self.llms[model_index]
            self.logger.info(f'Querying model: {self.model_names[model_index]}')
            problem = self.invoke_chat(f'Problem #{n + 1}', chat=llm,
                                       template=self.problem_templates.get_problem_selection_template())
            problems.append(problem)
        self.logger.info('Done')
        return problems

    @staticmethod
    def invoke_chat(name, chat, template, var_dict=None, log_result=True):
        if var_dict is None:
            var_dict = {}
        problem_selection_chain = template | chat
        st = now()
        response = problem_selection_chain.invoke(var_dict)
        time = now() - st
        result = response.content
        if log_result:
            Arena.logger.debug(f'{name}: {wrap(result)}\nTime: {time:.0f} sec')
        return result


def clean_json_result(json_like):
    if json_like[0] == '{':
        return json_like
    i1 = json_like.find('{')
    i2 = json_like.rfind('}')
    return json_like[i1:i2 + 1]
