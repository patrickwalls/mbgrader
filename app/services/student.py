from app import app, db
from ..models import Student


class StudentService:
    def __init__(self, s_id: int):
        self.s_id = s_id

    def create(self):
        student = Student(id=self.s_id)
        db.session.add(student)
        db.session.commit()