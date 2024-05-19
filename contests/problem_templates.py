from abc import abstractmethod

from langchain_core.prompts import ChatPromptTemplate


class ProblemTemplates:
    @abstractmethod
    def get_templates_set_name(self) -> str:
        pass

    @abstractmethod
    def get_problem_selection_template(self) -> ChatPromptTemplate:
        pass

    @abstractmethod
    def get_question_template(self) -> ChatPromptTemplate:
        pass

    @abstractmethod
    def get_answer_evaluation(self) -> ChatPromptTemplate:
        pass
