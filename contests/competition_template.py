from abc import abstractmethod
from typing import List

from langchain_core.prompts import ChatPromptTemplate


class CompetitionTemplate:
    @abstractmethod
    def get_template_id(self) -> str:
        pass

    @abstractmethod
    def get_template_name(self) -> str:
        pass

    @abstractmethod
    def get_metric_keys(self) -> List[str]:
        pass

    @abstractmethod
    def get_task_selection_template(self) -> ChatPromptTemplate:
        pass

    @abstractmethod
    def get_question_template(self) -> ChatPromptTemplate:
        pass

    @abstractmethod
    def get_answer_evaluation(self) -> ChatPromptTemplate:
        pass
