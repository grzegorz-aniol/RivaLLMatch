import os
import dotenv

import models

dotenv.load_dotenv()

from arena import Arena
from contests.problem_solving_templates import TaskSolvingTemplates
from result_reporter import ChartReporter

if __name__ == '__main__':
    llms = [
        models.get_open_ai_llm(),
        models.get_open_ai_llm(model='gpt-3.5-turbo-0125'),
        models.get_claude_llm(),
        models.get_llama3(),
        models.get_mixtral(),
        models.get_gemini_llm(),
    ]
    model_names = [models.get_model_name(llm) for llm in llms]

    arena = Arena(TaskSolvingTemplates(), llms, n_jobs=6)
    competition_scores = arena.run() # n_rounds=len(llms)

    reporter = ChartReporter('problem_solving', model_names, competition_scores)
    reporter.generate_reports()
