from typing import List

from ..models import Question


def get_questions_of_assignment(assignment_id: int) -> List[dict]:
    questions = Question.query.filter_by(assignment_id=assignment_id).all()
    return [q.to_dict() for q in questions]
