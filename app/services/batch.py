from app import app, db
from ..models import Batch, Response


class BatchService:
    def __init__(
        self,
        *,
        grade: int = None,
        comments: str = None,
        datatype_id: int = None,
        next_id: int = None,
        previous_id: int = None,
        question_id: int = None,
    ):
        self.grade = grade
        self.comments = comments
        self.datatype_id = datatype_id
        self.next_id = next_id
        self.previous_id = previous_id
        self.question_id = question_id

    def create(self) -> dict:
        new_batch = Batch(
            grade=self.grade,
            comments=self.comments,
            datatype_id=self.datatype_id,
            question_id=self.question_id,
            next_id=self.question_id,
            previous_id=self.previous_id,
        )
        db.session.add(new_batch)
        db.session.commit()
        return new_batch.to_dict()
