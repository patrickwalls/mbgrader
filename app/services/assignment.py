from pathlib import Path

from app import app, db
from ..models import (
    Assignment,
    Student,
    Submission,
    Response,
)
from ..selectors.datatype import get_datatype_from_extension


class AssignmentService:
    def __init__(self,
        *,
        name: str = None,
        folder_name: str = None,
        assignment_id: int = None
    ):
        self.name = name
        self.folder_name = name
        self.id = assignment_id

    def create(self) -> dict:
        new_model = Assignment(
            name=self.name, folder_name=self.folder_name
        )
        db.session.add(new_model)
        db.session.commit()
        self.id = new_model.id
        return new_model.to_dict()


    def load_submissions(self):
        assignment_dir = Path("submissions") / self.folder_name
        student_dirs = [d for d in assignment_dir.iterdir() if d.is_dir()]

        for s_dir in student_dirs:
            s_id = int(s_dir.stem)
            student = Student.query.get(s_id)
            if not student:
                student = Student(id=s_id)
            db.session.add(student)

            submission = Submission(
                assignment_id=self.id,
                student_id=s_id,
                grade=0,
                feedback="",
            )
            db.session.add(submission)

            for response_file in s_dir.iterdir():
                filename_split = response_file.name.split(".")
                var_name, extension = filename_split[0], filename_split[-1]
                var_name = var_name.lower()

                datatype = get_datatype_from_extension(extension)

                response = Response(
                    assignment_id=self.id,
                    student_id=s_id,
                    datatype_id=datatype.id,
                    var_name=var_name
                )
                db.session.add(response)

            db.session.commit()

    def delete(self):
        model = Assignment.query.get(self.id)
        if model:
            db.session.delete(model)
            db.session.commit()
