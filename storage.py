from typing import List, Type

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from entities.base import Base
from entities.competition_task import CompetitionTask
from entities.duel_result import DuelResult
from entities.experiment import Experiment


class Storage:

    def __init__(self, db_path):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.session = self.SessionLocal()

    def get_experiment(self) -> Experiment:
        return self.session.query(Experiment).get(0)

    def save_experiment(self, experiment: Experiment):
        experiment.id = 0
        self.session.add(experiment)
        self.session.commit()

    def delete_experiment(self):
        self.session.query(Experiment).delete()
        self.session.commit()

    def get_tasks(self) -> List[Type[CompetitionTask]]:
        return self.session.query(CompetitionTask).all()

    def save_task(self, task: CompetitionTask):
        self.session.add(task)
        self.session.commit()

    def save_duel_result(self, result: DuelResult):
        self.session.add(result)
        self.session.commit()

    def get_all_results(self) -> list[Type[DuelResult]]:
        return self.session.query(DuelResult).all()
