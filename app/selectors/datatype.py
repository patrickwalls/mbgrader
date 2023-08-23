from ..models import Datatype


def get_datatype_from_extension(extension: str) -> Datatype:
    return Datatype.query.filter_by(extension=extension).first()


def get_datatype_name(datatype_id: int) -> str:
    return Datatype.query.get(datatype_id).name
