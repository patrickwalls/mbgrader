from typing import List
from app import app, db
from ..models import Batch, Question


def get_batches_by_question(question_id: int) -> List[Batch]:
    batches = Question.query.get(question_id).batches
    return sorted(
        list(batches),
        key=lambda b: b.total_responses(),
        reverse=True,
    )
