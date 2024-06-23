from typing import List

from langchain_core.prompts import ChatPromptTemplate

from contests.competition_template import CompetitionTemplate


class CreativeWritingTemplate(CompetitionTemplate):
    """
        Set of prompt templates for creative writing competition
    """

    task_selection_template = ChatPromptTemplate.from_messages([
        ('user',
         """Find an idea or topic that can be used for creative writing task for another persona. 
         Your response should not contain any additional comments regarding the topic - return just an idea. 
         Do not use any instruction keywords in the output - just use plain text/sentences.""")
    ])

    problem_question_template = ChatPromptTemplate.from_messages([
        ('user', """You are presented with a creative writing task on specific topic which will be presented to you. 
        Provide the answer as a short story, poem, or descriptive passage, not longer than 512 words.
        Do not include in your answer any introduction, instructions or comments.

         Topic: {task}
         """)
    ])

    answer_evaluation_template = ChatPromptTemplate.from_messages([
        ('user', """You are a jury of creative writing competition. 
        Someone was asked to provide a short story, poem, or descriptive passage not longer than 512 words. 
        Your goal is to evaluate and score his work. 
        There are three criteria you will evaluate the answer: creativity, emotional depth and narrative flow.
        The score for each criteria should be a value in range between 0.0 and 1.0. 
        The output should be just json document, with map containing each criteria and the score value. 
        Use following keys for the response map: 'creativity', 'depth', 'flow'.
        Do not use any formatting in the output - return just JSON document with scores. 
        Do not output any additional comments regarding the answer.         
        Example of an output: {{"creativity": 0.61, "depth": 0.82, "flow": 0.55}}  

        Creative writing topic: {task}

        Problem answer to evaluate: {answer}
        """)
    ])

    def get_template_id(self) -> str:
        return 'creative_writing'

    def get_template_name(self) -> str:
        return 'Creative Writing'

    def get_metric_keys(self) -> List[str]:
        return ['creativity', 'depth', 'flow']

    def get_task_selection_template(self) -> ChatPromptTemplate:
        return CreativeWritingTemplate.task_selection_template

    def get_question_template(self) -> ChatPromptTemplate:
        return CreativeWritingTemplate.problem_question_template

    def get_answer_evaluation(self) -> ChatPromptTemplate:
        return CreativeWritingTemplate.answer_evaluation_template
