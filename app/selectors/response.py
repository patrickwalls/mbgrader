from app import app, db
from ..models import Response


def get_response(
    assignment_id: int,
    student_id: int,
    var_name: str,
) -> Response:
    response = Response.query.filter_by(
        assignment_id=assignment_id,
        student_id=student_id,
        var_name=var_name,
    ).first()
    return response
