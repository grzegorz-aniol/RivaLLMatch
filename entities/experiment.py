from sqlalchemy import Column, Integer, JSON, String, Boolean

from entities.base import Base


class Experiment(Base):
    __tablename__ = 'experiment'
    id = Column(Integer, primary_key=True)
    created_ts = Column(Integer, nullable=False)
    initialized = Column(Boolean, nullable=False, default=False)
    template_id = Column(String, nullable=False)
    model_names = Column(JSON, nullable=False)
    n_rounds = Column(Integer, nullable=False)
    n_pairs_in_round = Column(Integer, nullable=False)
    n_duels =  Column(Integer, nullable=False)
