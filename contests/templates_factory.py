from contests.competition_template import CompetitionTemplate
from contests.creative_writing_template import CreativeWritingTemplate
from contests.task_solving_template import ProblemSolvingTemplate


def build_competition_template(templates_id) -> CompetitionTemplate:
    all_objs = [CreativeWritingTemplate(), ProblemSolvingTemplate()]
    for obj in all_objs:
        if obj.get_template_id() == templates_id:
            return obj
    raise Exception(f'Unknown template id "{templates_id}"')
