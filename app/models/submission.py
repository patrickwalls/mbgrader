from app import db

class Submission(db.Model):
    grade = db.Column(db.Integer)
    feedback = db.Column(db.String(280))

    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    student = db.relationship('Student', backref='submissions', lazy=True)
