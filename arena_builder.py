import random
import time
from itertools import permutations
from typing import List

from contests.templates_factory import build_competition_template
from entities.competition_task import CompetitionTask
from entities.experiment import Experiment
from job_queue import DuelsQueue
from logger import Logger
from messages.duel_request_message import DuelRequestMessage
from models import build_model, get_model_name
from resumable_arena import ResumableArena
from storage import Storage


class ArenaBuilder:
    logger = Logger()

    def __init__(self, n_rounds: int, model_names: List[str], template_id: str, storage: Storage, duels_queue: DuelsQueue):
        self.n_rounds = n_rounds
        self.model_names = model_names
        self.original_model_names = model_names.copy()
        self.template_id = template_id
        self.competition_template = build_competition_template(template_id)
        self.storage = storage
        self.duels_queue = duels_queue
        self.llms = None

    def create(self):
        is_new = self.__initialize_new_experiment()
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
            self.logger.info(
                'WARN: Processing queue for the experiment is empty. It seems the experiment is completed.')
        self.llms = [build_model(model) for model in experiment.model_names]

    def __initialize_new_experiment(self):
        experiment = self.storage.get_experiment()
        if experiment and experiment.initialized:
            return False
        self.logger.info('Initializing a new experiment.')
        if experiment:
            self.storage.delete_experiment()

        self.llms = [build_model(model) for model in self.model_names]
        # re-create model names with formal names used in created objects
        self.model_names = [get_model_name(model) for model in self.llms]

        n_llms = len(self.model_names)
        if n_llms < 2:
            raise Exception('Too small number of LLMs. At least two should be provided to start a competition.')
        all_pairs = list(permutations(self.model_names, 2))
        n_pairs_in_round = len(all_pairs)
        n_duels = self.n_rounds * n_pairs_in_round

        experiment = Experiment()
        experiment.template_id = self.template_id
        experiment.model_names = self.original_model_names
        experiment.created_ts = time.time_ns() // 1_000
        experiment.n_rounds = self.n_rounds
        experiment.n_pairs_in_round = n_pairs_in_round
        experiment.n_duels = n_duels
        self.storage.save_experiment(experiment)

        tasks = self.__build_tasks(n_llms)
        self.__build_duel_requests(experiment, tasks, all_pairs)

        experiment.initialized = True
        self.storage.save_experiment(experiment)
        return True

    def __build_tasks(self, n_tasks):
        n_llms = len(self.model_names)
        if not (n_tasks >= n_llms and n_tasks % n_llms == 0):
            raise AssertionError('Number of tasks should be a multiple of the number of models.')
        self.logger.info(f'Models under evaluation: {self.model_names}')
        self.logger.info(f'Generate {n_tasks} tasks for the competition.')
        tasks = []
        for n in range(n_tasks):
            model_index = n % n_llms
            original_model_name = self.original_model_names[model_index]
            llm = self.llms[model_index]
            self.logger.info(f'Querying model: {original_model_name}')

            try:
                task = ResumableArena.invoke_chat(f'Task #{n + 1}', chat=llm,
                                                  template=self.competition_template.get_task_selection_template())
            except Exception as ex:
                raise Exception(f'Cannot get task from the model {original_model_name}. Error: {ex}')

            competition_task = CompetitionTask()
            competition_task.task_description = task
            competition_task.created_by_model = original_model_name
            self.storage.save_task(competition_task)

            tasks.append(task)
        self.logger.info('Done')
        return tasks

    def __build_duel_requests(self, experiment: Experiment, tasks, all_pairs):
        self.logger.info(f'Scheduling duels for competition: {self.competition_template.get_template_name()}')
        self.logger.info(f'Number of rounds: {self.n_rounds}')
        self.logger.info(f'Number of duels: {experiment.n_duels} ({experiment.n_pairs_in_round} in each round)')

        n_llms = len(self.llms)
        for n in range(self.n_rounds):
            self.logger.info(f'.. round {n + 1}')
            for master_model, student_model in all_pairs:
                task_index = random.randrange(0, n_llms)
                task = tasks[task_index]
                duel_request = DuelRequestMessage(master_model=master_model, student_model=student_model,
                                                  template_id=self.template_id, task=task, task_num=task_index+1)
                self.duels_queue.add(duel_request)

    @staticmethod
    def __check_missing(variable, attribute_name):
        if not variable:
            raise Exception(f"Didn't find an existing experiment. Missing {attribute_name} list. "
                            "You need to specify one to run new experiment")
