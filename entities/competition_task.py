from sqlalchemy import Column, Integer, String

from entities.base import Base


class CompetitionTask(Base):
    __tablename__ = 'competition_task'
    id = Column(Integer, primary_key=True)
    task_description = Column(String, nullable=False)
    created_by_model = Column(String, nullable=False)
