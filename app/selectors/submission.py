from typing import List
from app import app, db
from ..models import Submission


def get_submissions_for_assignment(assignment_id: int) -> List[Submission]:
    return Submission.query.filter_by(assignment_id=assignment_id)
