import dotenv

from arena_builder import ArenaBuilder
from job_queue import DuelsQueue
from storage import Storage

dotenv.load_dotenv()

from result_reporter import ChartReporter
import argparse


class RivaLLMatch:
    model_names = [
        # 'gpt-4o',
        # 'gpt-3.5-turbo-0125',
        'claude-3-opus-20240229',
        'claude-3-5-sonnet-20240620',
        'llama3-8b-8192',
        'llama3-70b-8192',
        # 'gemma-7b-it',
        'mixtral-8x7b-32768',
        # 'gemini-1.0-pro-latest',
        # 'gemini-1.5-pro-latest',
    ]

    def __init__(self):
        parser = argparse.ArgumentParser(description="Parse command line arguments for an experiment.")
        parser.add_argument('--experiment_id', type=str, required=True,
                            help="Experiment ID (required)")
        parser.add_argument('--template_id', type=str,
                            help="Experiment prompt's template ID (required for new experiment)")
        parser.add_argument('--models', type=lambda s: s.split(','),
                            help="List of comma separated model namesLLMs (required for new experiment)")
        self.args = parser.parse_args()
        self.db_path = f"./{self.args.experiment_id}.db"
        self.storage = Storage(db_path=self.db_path)
        self.duels_queue = DuelsQueue(db_path=self.db_path)

    def run(self):
        model_names = RivaLLMatch.model_names
        n_llms = len(model_names)
        arena = (ArenaBuilder(model_names,
                              self.args.template_id,
                              self.storage,
                              self.duels_queue)
                 .create())
        competition_scores = arena.run(n_jobs=n_llms)
        reporter = ChartReporter(self.args.template_id, model_names, competition_scores)
        reporter.generate_reports()


if __name__ == '__main__':
    rival_match = RivaLLMatch()
    rival_match.run()
