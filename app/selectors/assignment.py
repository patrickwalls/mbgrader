from typing import List

from ..models import Assignment, Response


def get_all_assignments() -> List[dict]:
    assignments = Assignment.query.all()
    return [instance.to_dict() for instance in assignments]


def get_assignment(assignment_id: int) -> dict:
    assignment = Assignment.query.get_or_404(assignment_id)
    return assignment.to_dict()


def get_assignment_vars(assignment_id: int) -> List[str]:
    responses = Response.query.filter_by(assignment_id=assignment_id).all()
    response_list = list(set([response.var_name.lower() for response in responses]))
    response_list.sort()
    return response_list
