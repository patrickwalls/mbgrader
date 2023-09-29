from typing import List
from app import app, db
from ..models import Question, BatchResponse
from ..services.batch import BatchService
from ..selectors.submission import get_submissions_for_assignment
from ..selectors.response import get_response
from ..selectors.batch import get_batches_by_question


class QuestionService:
    def __init__(
        self,
        *,
        name: str = None,
        var_name: str = None,
        alt_var_name: str = None,
        max_grade: int = None,
        tolerance: float = None,
        preprocessing: str = None,
        assignment_id: int = None,
        question_id: int = None,
    ):
        self.name = name
        self.var_name = var_name
        self.alt_var_name = alt_var_name
        self.max_grade = max_grade
        self.tolerance = tolerance
        self.preprocessing = preprocessing
        self.assignment_id = assignment_id
        self.id = question_id
    
    def create(self) -> dict:
        max_grade = self.max_grade or 1
        tolerance = self.tolerance or 0.0001

        question = Question(
            name=self.name,
            var_name=self.var_name,
            alt_var_name=self.alt_var_name,
            max_grade=max_grade,
            tolerance=tolerance,
            preprocessing = self.preprocessing,
            assignment_id=self.assignment_id,
        )
        db.session.add(question)
        db.session.commit()
        return question.to_dict()

    def delete(self):
        question = Question.query.get(self.id)
        if question:
            db.session.delete(question)
            db.session.commit()

    def delete_batches(self):
        question = Question.query.get(self.id)
        if question:
            for batch in question.batches:
                db.session.delete(batch)
            db.session.commit()

    def create_batches(self) -> List[dict]:
        question = Question.query.get(self.id)
        if question.preprocessing:
            fun = question.get_preprocessing()
        else:
            fun = None
        
        submissions = get_submissions_for_assignment(self.assignment_id)
        for submission in submissions:
            status = "Response loaded successfully."
            response = get_response(
                self.assignment_id,
                submission.student_id,
                var_name=self.var_name
            )

            if not response:
                alt_vars = self.alt_var_name.lower().split(",")
                for alt_var in alt_vars:
                    response = get_response(
                        self.assignment_id,
                        submission.student_id,
                        var_name=self.var_name,
                    )
                    if response:
                        status = "Response loaded successfully. But variable name is misspelled!"
                        break

            if not response:
                continue

            batched = False
            for batch in question.batches:
                service = BatchService(batch_id=batch.id)
                if service.compare(response, preprocessing=fun):
                    batched = True
                    continue
            if not batched:
                new_batch_service = BatchService(
                    grade=0,
                    comments="",
                    datatype_id=response.datatype.id,
                    question_id=self.id,
                    next_id=0,
                    previous_id=0
                )
                new_batch_service.create()
            batch_response = BatchResponse(
                response_id=response.id,
                batch_id=new_batch_service.id,
                status=status,
            )
            db.session.add(batch_response)
            db.session.commit()

        batches = get_batches_by_question(self.id)
        for n, batch in enumerate(batches):
            next_batch_index = (n + 1) % len(batches)
            batch.next_id = batches[next_batch_index].id
            previous_batch_index = (n - 1) % len(batches)
            batch.previous_id = batches[previous_batch_index].id
            db.session.add(batch)
            db.session.commit()

        return [b.to_dict() for b in batches]
