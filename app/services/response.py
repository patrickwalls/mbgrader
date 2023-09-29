from pathlib import Path
from app import app, db
from ..models import Response, Assignment
from ..selectors.datatype import get_datatype_from_extension


class ResponseService:
    def __init__(
        self,
        *,
        var_name: str = None,
        assignment_id: int = None,
        extension = str,
        student_id: int = None,
    ):
        self.var_name = var_name.lower()
        self.assignment_id = assignment_id
        self.extension = extension
        self.student_id = student_id

    def create(self) -> Response:
        datatype = get_datatype_from_extension(self.extension)
        new_response = Response(
            assignment_id=self.assignment_id,
            student_id=self.student_id,
            datatype_id=datatype.id,
            var_name=self.var_name,
        )
        db.session.add(new_response)
        db.session.commit()
        return new_response
    