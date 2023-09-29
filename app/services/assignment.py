from pathlib import Path
from typing import List
import numpy as np

from app import app, db
from ..models import (
    Assignment,
    Student,
    Submission,
    Response,
)
from ..services.response import ResponseService
from ..selectors.datatype import get_datatype_from_extension
from ..selectors.response import get_response


class AssignmentService:
    def __init__(
        self,
        *,
        name: str = None,
        folder_name: str = None,
        assignment_id: int = None
    ):
        self.name = name
        self.folder_name = folder_name
        self.id = assignment_id

    def create(self) -> dict:
        new_model = Assignment(
            name=self.name, folder_name=self.folder_name
        )
        db.session.add(new_model)
        db.session.commit()
        self.id = new_model.id  # TODO: assignment id init kwarg is ignored (assumed to be none for now)
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

    def create_responses(
        self,
        var_name: str,
        vars: List[str],
        expression: str,
        extension: str,
    ):
        func = eval(expression)
        submissions = Assignment.query.get(self.id).submissions
        for submission in submissions:
            student_id = submission.student_id
            student_responses = []
            for var in [v.lower() for v in vars]:
                response = get_response(
                    self.id, student_id, var
                )
                if response:
                    student_responses.append(response.get_data())
            
            try:
                value = func(student_responses)
                print(value)
            except Exception as e:
                error_response_service = ResponseService(
                    var_name=var_name.lower(),
                    assignment_id=self.id,
                    extension="txt",
                    student_id=student_id,
                )
                error_response = error_response_service.create()
                filepath = error_response.get_fullfile()
                with open(filepath, "w") as f:
                    f.write(f"{e}")
                continue

            new_response_service = ResponseService(
                var_name=var_name.lower(),
                assignment_id=self.id,
                student_id=student_id,
                extension=extension,
            )
            new_response = new_response_service.create()
            filepath = new_response.get_fullfile()
            np.savetxt(filepath, value, fmt="%.5f", delimiter="")
