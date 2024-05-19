from langchain_core.prompts import ChatPromptTemplate

from contests.problem_templates import ProblemTemplates


class ProblemSolvingTemplates(ProblemTemplates):
    """
        Set of prompt templates for problem-solving competition
    """

    problem_selection_template = ChatPromptTemplate.from_messages([
        ('user',
         """Find a question that may be asked to another persona, in order to evaluates his problem-solving skills.
         The problem or question should be complex and will require a detailed explanation or solution. The response 
         should not contain any comments regarding the problem. Just definition of the problem. Do not use any 
         instruction keywords in the output, just use plain text/sentences.""")
    ])

    problem_question_template = ChatPromptTemplate.from_messages([
        ('user', """You are a part of of problem-solving competition. A problem or a question will be presented to you.
        You should provide a comprehensive solution/answer to the problem. Your answer will be later evaluated and
         scored by someone else. The answer should contain just the solution, do not provide any introduction.

         Problem: {problem}
         """)
    ])

    answer_evaluation_template = ChatPromptTemplate.from_messages([
        ('user', """You are a jury of problem-solving competition. Someone was asked to solve a problem 
        and he provided a solution (answer). Your goal is to evaluate and score his answer. There are for criteria
        you will evaluate the answer: accuracy, clarity, depth or explanation and logical reasoning. For each criteria
        provide the score as a value in range between 0.0 and 1.0. The output should be just json document, with
        map containing each criteria and the score value. Use following keys for the response map: 'accuracy', 
        'clarity', 'depth', 'reasoning'. Do not use any formatting in the output. Just pure JSON document. 
        Do not output any additional comments regarding the answer. 

        Problem: {problem}

        Answer to evaluate: {answer}
        """)
    ])

    def get_templates_set_name(self) -> str:
        return 'Problem Solving'

    def get_problem_selection_template(self) -> ChatPromptTemplate:
        return ProblemSolvingTemplates.problem_selection_template

    def get_question_template(self) -> ChatPromptTemplate:
        return ProblemSolvingTemplates.problem_question_template

    def get_answer_evaluation(self) -> ChatPromptTemplate:
        return ProblemSolvingTemplates.answer_evaluation_template
