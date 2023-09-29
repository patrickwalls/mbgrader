from app import db

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    folder_name = db.Column(db.String(80), unique=True, nullable=False)

    questions = db.relationship('Question', backref='assignment', lazy=True, cascade='all,delete')
    responses = db.relationship('Response', backref='assignment', lazy=True, cascade='all,delete')
    submissions = db.relationship('Submission', backref='assignment', lazy=True, cascade='all,delete')

    def total_points(self):
        points = [question.max_grade for question in self.questions]
        return sum(points)

    def total_submissions(self):
        return len(self.submissions)

    def total_questions(self):
        return len(self.questions)
        
    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'folder_name': self.folder_name,
                'total_points': self.total_points(),
                'total_questions': self.total_questions(),
                'total_submissions': self.total_submissions()}
