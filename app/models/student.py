from app import db


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    responses = db.relationship('Response', backref='student', lazy=True)
