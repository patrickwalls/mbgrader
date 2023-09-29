from app import db

class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer)
    comments = db.Column(db.String(280))
    next_id = db.Column(db.Integer)
    previous_id = db.Column(db.Integer)

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    datatype_id = db.Column(db.Integer, db.ForeignKey('datatype.id'), nullable=False)
    batch_responses = db.relationship('BatchResponse', backref='batch', lazy=True, cascade='all,delete')

    def total_responses(self):
        return len(self.batch_responses)

    def get_fullfile(self):
        return self.batch_responses[0].response.get_fullfile()

    def get_data(self):
        return self.batch_responses[0].response.get_data()

    def to_dict(self):
        from ..selectors.datatype import get_datatype_name

        datatype = get_datatype_name(self.datatype_id)
        if self.question.preprocessing:
            fun = self.question.get_preprocessing()
            try:
                data = fun(self.batch_responses[0].response.student_id,self.get_data())
            except:
                data = self.get_data()
        else:
            data = self.get_data()
        if datatype == 'figure':
            dataJSON = []
            for line in data:
                if line.size == 2:
                    dataJSON.append(line.tolist())
                else:
                    dataJSON.append({'x': line[:,0].tolist(),'y': line[:,1].tolist()})
        else:
            dataJSON = str(data)
        return {'id': self.id,
                'grade': self.grade,
                'comments': self.comments,
                'question_id': self.question_id,
                'assignment_id': self.question.assignment.id,
                'datatype': datatype,
                'total_batch_responses': self.total_responses(),
                'total_question_responses': self.question.total_responses(),
                'next_id': self.next_id,
                'previous_id': self.previous_id,
                'data': dataJSON}
