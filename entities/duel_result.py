from sqlalchemy import Column, Integer, String, JSON

from entities.base import Base


class DuelResult(Base):
    __tablename__ = 'duel_result'
    id = Column(Integer, primary_key=True)
    created_ts = Column(Integer, nullable=False)
    task_num = Column(Integer, nullable=False)
    scores_json = Column(JSON, nullable=False)
    master_model = Column(String, nullable=False)
    student_model = Column(String, nullable=False)
