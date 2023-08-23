from app import db


class Datatype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    extension = db.Column(db.String(10), nullable=False)

    batches = db.relationship('Batch', backref='datatype', lazy=True)
    responses = db.relationship('Response', backref='datatype', lazy=True)
