from typing import List

from langchain_core.prompts import ChatPromptTemplate

from contests.competition_template import CompetitionTemplate


class DebateTemplate(CompetitionTemplate):

    task_selection_template = ChatPromptTemplate.from_messages([
        ('user',
         """Generate a thesis that will be used in a debate and persuasion task. 
         Do not include any introduction, hints, header, formatting or pre-phrase.
         Return just a plain thesis, clearly explaining what the opponent should debate for or against.""")
    ])

    problem_question_template = ChatPromptTemplate.from_messages([
        ('user',
         """You are participating in a debate and you should opting for the following thesis:
          {task}
          
          Make sure your argument is well-structured, evidence-based, and persuasive.
          Your answer should be rather concise than too verbose.
          """)
    ])

    answer_evaluation_template = ChatPromptTemplate.from_messages([
        ('user',
         """You are an expert evaluator assessing the effectiveness of an argument presented in a debate.
         
         The thesis you will receive arguments for is: {task}
         
         The answer in the competition is: {answer}

         There are 4 criteria you will evaluate the answer. 
         Here is the list with its corresponding keys used in the output: 
         * clarity and structure (key: clarity)
         * evidence and support (key: evidence)
         * persuasiveness (key: persuasiveness)
         * addressing counterarguments (key: anticipation).          
         
         The score for each criteria should be a value in range between 0.0 and 1.0. 
         The output should be just json document, with map containing each criteria key and the score value. 
         Do not use any formatting in the output - return just JSON document with scores. 
         Do not output any additional comments regarding the answer.         
         Example of an output: {{"clarity": 0.61, "evidence": 0.82, "persuasiveness": 0.55, "anticipation": 0.2}}  
         """)
    ])

    def get_template_id(self) -> str:
        return 'debate_persuasion'

    def get_template_name(self) -> str:
        return 'Debate and persuasion'

    def get_metric_keys(self) -> List[str]:
        return ['clarity', 'evidence', 'persuasiveness', 'anticipation']

    def get_task_selection_template(self) -> ChatPromptTemplate:
        return DebateTemplate.task_selection_template

    def get_question_template(self) -> ChatPromptTemplate:
        return DebateTemplate.problem_question_template

    def get_answer_evaluation(self) -> ChatPromptTemplate:
        return DebateTemplate.answer_evaluation_template