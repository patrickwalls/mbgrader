from ..models import Datatype


def get_datatype_from_extension(extension: str) -> Datatype:
    return Datatype.query.filter_by(extension=extension).first()
