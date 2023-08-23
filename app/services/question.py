from app import app, db
from ..models import Question


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
