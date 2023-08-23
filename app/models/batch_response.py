from app import db


class BatchResponse(db.Model):
    response_id = db.Column(db.Integer, db.ForeignKey('response.id'), primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), primary_key=True)
    status = db.Column(db.String(140))

    response = db.relationship('Response', backref='batch_responses', lazy=True)
