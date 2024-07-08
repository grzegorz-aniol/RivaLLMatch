from contests.competition_template import CompetitionTemplate
from contests.creative_writing_template import CreativeWritingTemplate
from contests.debate_template import DebateTemplate
from contests.task_solving_template import ProblemSolvingTemplate


def get_all_templates():
    return [CreativeWritingTemplate(), ProblemSolvingTemplate(), DebateTemplate()]


def build_competition_template(templates_id) -> CompetitionTemplate:
    for obj in get_all_templates():
        if obj.get_template_id() == templates_id:
            return obj
    raise Exception(f'Unknown template id "{templates_id}"')
