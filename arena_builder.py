import random
import time
from itertools import permutations

from contests.templates_factory import build_competition_template
from entities.competition_task import CompetitionTask
from entities.experiment import Experiment
from job_queue import DuelsQueue
from logger import Logger
from messages.duel_request_message import DuelRequestMessage
from models import build_model
from resumable_arena import ResumableArena
from storage import Storage


class ArenaBuilder:
    logger = Logger()

    def __init__(self, model_names, template_id, storage: Storage, duels_queue: DuelsQueue):
        self.model_names = model_names
        self.template_id = template_id
        self.competition_template = build_competition_template(template_id)
        self.storage = storage
        self.duels_queue = duels_queue
        self.llms = None

    def create(self):
        is_new = self.__initialize_new_experiment(n_rounds=len(self.model_names))
        if not is_new:
            self.__initialize_with_existing_experiment()

        arena = ResumableArena(self.storage, self.duels_queue, self.competition_template,
                               self.llms)
        return arena

    def __initialize_with_existing_experiment(self):
        self.logger.info('Continue existing experiment.')
        experiment = self.storage.get_experiment()
        if self.template_id != experiment.template_id:
            raise Exception(f'Experiment is created with template "{experiment.template_id}" '
                            f'but the application is executed with "{self.template_id}". '
                            f'You need to finish previous experiment first.')
        if self.duels_queue.queue.qsize() == 0:
            raise Exception('Processing queue for the experiment is empty. It seems the experiment is completed.')
        self.llms = [build_model(model) for model in experiment.model_names]

    def __initialize_new_experiment(self, n_rounds=1, n_random_pairs=None):
        experiment = self.storage.get_experiment()
        if experiment and experiment.initialized:
            return False
        self.logger.info('Initializing a new experiment.')
        if experiment:
            self.storage.delete_experiment()
        experiment = Experiment()
        experiment.template_id = self.template_id
        experiment.model_names = self.model_names
        experiment.created_ts = time.time_ns() // 1_000
        self.storage.save_experiment(experiment)

        self.llms = [build_model(model) for model in self.model_names]

        n_llms = len(self.model_names)
        if n_llms < 2:
            raise Exception('Too small number of LLMs. At least two should be provided to start a competition.')
        all_pairs = list(permutations(self.model_names, 2))
        n_pairs_in_round = n_random_pairs if n_random_pairs else len(all_pairs)

        self.logger.info(f'Starting competition: {self.competition_template.get_template_name()}')
        self.logger.info(f'Number of rounds: {n_rounds}')
        self.logger.info(f'Number of duels: {n_rounds * n_pairs_in_round} ({n_pairs_in_round} in each round)')
        self.logger.info(f'Models under evaluation: {self.model_names}')
        self.logger.info('')

        tasks = self.__build_tasks(n_rounds)
        self.__build_duel_requests(tasks, all_pairs, n_random_pairs,
                                   n_rounds)

        experiment.initialized = True
        self.storage.save_experiment(experiment)
        return True

    def __build_tasks(self, n_tasks):
        self.logger.info('Generate list of tasks')
        n_llms = len(self.model_names)
        tasks = []
        for n in range(n_tasks):
            model_index = n % n_llms
            model_name = self.model_names[model_index]
            llm = self.llms[model_index]
            self.logger.info(f'Querying model: {model_name}')
            task = ResumableArena.invoke_chat(f'Task #{n + 1}', chat=llm,
                                              template=self.competition_template.get_task_selection_template())
            competition_task = CompetitionTask()
            competition_task.task_description = task
            competition_task.created_by_model = model_name
            self.storage.save_task(competition_task)

            tasks.append(task)
        self.logger.info('Done')
        return tasks

    def __build_duel_requests(self, tasks, all_pairs, n_random_pairs, n_rounds=1):
        self.logger.info('Scheduling all duels...')
        for n in range(n_rounds):
            self.logger.info('-------------------------------------------------------------------------------')
            self.logger.info(f'Round: {n + 1}')
            task_index = n
            pairs_in_round = all_pairs if n_random_pairs is None else random.sample(all_pairs, n_random_pairs)
            for master_model, student_model in pairs_in_round:
                task = tasks[task_index]
                duel_request = DuelRequestMessage(master_model=master_model, student_model=student_model,
                                                  template_id=self.template_id, task=task)
                self.duels_queue.add(duel_request)

    @staticmethod
    def __check_missing(variable, attribute_name):
        if not variable:
            raise Exception(f"Didn't find an existing experiment. Missing {attribute_name} list. "
                            "You need to specify one to run new experiment")
