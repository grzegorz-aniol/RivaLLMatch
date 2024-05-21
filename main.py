import dotenv

import models
from contests.creative_writing_templates import CreativeWritingTemplates
from contests.problem_solving_templates import TaskSolvingTemplates

dotenv.load_dotenv()

from arena import Arena
from result_reporter import ChartReporter

if __name__ == '__main__':
    llms = [
        models.get_open_ai_llm(),
        models.get_open_ai_llm(model='gpt-3.5-turbo-0125'),
        models.get_claude_llm(),
        models.get_llama3(),
        models.get_mixtral(),
        models.get_gemini_llm(model='gemini-1.0-pro-latest'),
        # models.get_gemini_llm(model='gemini-1.5-pro-latest'),
    ]
    model_names = [models.get_model_name(llm) for llm in llms]
    n_llms = len(llms)

    competition_templates = [
        TaskSolvingTemplates(),
        # CreativeWritingTemplates()
    ]

    for templates in competition_templates:
        arena = Arena(templates, llms)
        competition_scores = arena.run(n_rounds=n_llms, n_jobs=n_llms)
        # competition_scores = arena.run(n_rounds=1, n_jobs=n_llms, n_random_pairs=5)
        reporter = ChartReporter(templates.get_templates_set_id(), model_names, competition_scores)
        reporter.generate_reports()
