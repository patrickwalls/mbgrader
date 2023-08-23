from app import db
import importlib


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    var_name = db.Column(db.String(80), nullable=False)
    alt_var_name = db.Column(db.String(80), nullable=False)
    max_grade = db.Column(db.Integer, default=0)
    tolerance = db.Column(db.Float, default=0.001)
    preprocessing = db.Column(db.String(280))

    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    batches = db.relationship('Batch', backref='question', lazy=True, cascade='all,delete')

    def get_preprocessing(self):
        f = open('preprocessing_module.py','w')
        f.write(self.preprocessing)
        f.close()
        import preprocessing_module
        importlib.reload(preprocessing_module)
        os.remove('preprocessing_module.py')
        return preprocessing_module.fun

    def total_batches(self):
        return len(self.batches)

    def total_responses(self):
        return sum([len(batch.batch_responses) for batch in self.batches])

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'var_name': self.var_name,
                'alt_var_name': self.alt_var_name,
                'max_grade': self.max_grade,
                'tolerance': self.tolerance,
                'assignment_id': self.assignment_id,
                'total_batches': self.total_batches(),
                'total_responses': self.total_responses()}
