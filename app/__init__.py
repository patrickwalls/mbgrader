from flask import Flask, render_template, jsonify, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

import os
from glob import glob
import numpy as np
import pandas as pd
import importlib
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

##################################################
## API
##################################################

@app.route('/assignments', methods=['GET','POST'])
def assignments():
    if request.method == 'GET':
        assignments = Assignment.query.all()
        return jsonify([assignment.to_dict() for assignment in assignments])
    elif request.method == 'POST':
        assignment = Assignment(name=request.json['name'])
        db.session.add(assignment)
        db.session.commit()
        assignment.load_submissions()
        return jsonify(assignment.to_dict())

@app.route('/assignments/<int:assignment_id>', methods=['GET','DELETE'])
def assignment(assignment_id):
    if request.method == 'GET':
        assignment = Assignment.query.get_or_404(assignment_id)
        return jsonify(assignment.to_dict())
    if request.method == 'DELETE':
        assignment = Assignment.query.get(assignment_id)
        if assignment:
            db.session.delete(assignment)
            db.session.commit()
            return ('',204)
        else:
            return ('',204)

@app.route('/assignments/<int:assignment_id>/grades')
def grades(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    assignment.save_grades()
    return ('',200)

@app.route('/assignments/<int:assignment_id>/vars')
def vars(assignment_id):
    responses = Response.query.filter_by(assignment_id=assignment_id).all()
    vars = sorted(list(set([response.var_name.lower() for response in responses])))
    return jsonify({'vars': vars})

@app.route('/assignments/<int:assignment_id>/questions', methods=['GET','POST'])
def questions(assignment_id):
    if request.method == 'GET':
        questions = Question.query.filter_by(assignment_id=assignment_id).all()
        return jsonify([question.to_dict() for question in questions])
    elif request.method == 'POST':
        question = Question(name=request.json['name'],
                            var_name=request.json['var_name'].lower(),
                            alt_var_name=request.json['alt_var_name'].lower(),
                            max_grade=request.json['max_grade'],
                            tolerance=request.json['tolerance'],
                            preprocessing=request.json['preprocessing'],
                            assignment_id=assignment_id)
        db.session.add(question)
        db.session.commit()
        return jsonify(question.to_dict())

@app.route('/assignments/<int:assignment_id>/questions/<int:question_id>', methods=['GET','DELETE'])
def question(assignment_id,question_id):
    if request.method == 'GET':
        question = Question.query.get_or_404(question_id)
        return jsonify(question.to_dict())
    if request.method == 'DELETE':
        question = Question.query.get(question_id)
        if question:
            db.session.delete(question)
            db.session.commit()
            return ('',204)
        else:
            return ('',204)

@app.route('/assignments/<int:assignment_id>/response', methods=['POST'])
def create_response(assignment_id):
    var_name = request.form['name']
    vars = request.form['vars'].split(',')
    expression = request.form['expression']
    extension = request.form['extension']
    assignment = Assignment.query.get_or_404(assignment_id)
    assignment.create_response(var_name,vars,expression,extension)
    return ('',200)

@app.route('/assignments/<int:assignment_id>/questions/<int:question_id>/batches', methods=['GET'])
def batch(assignment_id,question_id):
    create = request.args.get('create')
    if request.method == 'GET' and create == 'true':
        question = Question.query.get_or_404(question_id)
        question.delete_batches()
        question.create_batches()
        return jsonify([batch.to_dict() for batch in question.batches])
    elif request.method == 'GET' and create == 'false':
        question = Question.query.get_or_404(question_id)
        return jsonify([batch.to_dict() for batch in question.batches])

@app.route('/assignments/<int:assignment_id>/questions/<int:question_id>/batches/<int:batch_id>', methods=['GET','PUT'])
def grade(assignment_id,question_id,batch_id):
    if request.method == 'GET':
        batch = Batch.query.get_or_404(batch_id)
        return jsonify(batch.to_dict())
    elif request.method == 'PUT':
        batch = Batch.query.get_or_404(batch_id)
        batch.grade = int(request.json['grade'])
        batch.comments = request.json['comments']
        db.session.add(batch)
        db.session.commit()
        return jsonify(batch.to_dict())

##################################################
## DATABASE
##################################################

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    questions = db.relationship('Question', backref='assignment', lazy=True, cascade='all,delete')
    responses = db.relationship('Response', backref='assignment', lazy=True, cascade='all,delete')
    submissions = db.relationship('Submission', backref='assignment', lazy=True, cascade='all,delete')

    def load_submissions(self):
        student_ids = [int(os.path.basename(s)) for s in glob(os.path.join('submissions',self.name,'*'))]
        for student_id in student_ids:
            student = Student.query.get(student_id)
            if not student:
                student = Student(id=student_id)
            db.session.add(student)
            submission = Submission(assignment_id=self.id,student_id=student_id,grade=0,feedback='')
            db.session.add(submission)
            response_files = [os.path.basename(r) for r in glob(os.path.join('submissions',self.name,str(student_id),'*'))]
            for response_file in response_files:
                response_file_split = response_file.split('.')
                var_name, extension = response_file_split[0], response_file_split[-1]
                var_name = var_name.lower()
                datatype = Datatype.query.filter_by(extension=extension).first()
                response = Response(assignment_id=self.id,student_id=student_id,datatype_id=datatype.id,var_name=var_name)
                db.session.add(response)
            db.session.commit()

    def create_response(self,var_name,vars,expression,extension):
        fun = eval(expression)
        for submission in self.submissions:
            student_id = submission.student_id
            filename = os.path.join('submissions',self.name,str(student_id),var_name + '.' + extension)
            student_responses = []
            for var in [v.lower() for v in vars]:
                response = Response.query.filter_by(assignment_id=self.id,student_id=student_id,var_name=var).first()
                if response:
                    student_responses.append(response.get_data())
                else:
                    student_responses.append(None)
            try:
                value = fun(student_responses)
            except:
                text_datatype = Datatype.query.filter_by(extension='txt').first()
                filename = os.path.join('submissions',self.name,str(student_id),var_name + '.txt')
                f = open(filename,'w')
                f.write('Error')
                f.close()
                new_response = Response(assignment_id=self.id,student_id=student_id,datatype_id=text_datatype.id,var_name=var_name.lower())
                db.session.add(new_response)
                db.session.commit()
                continue
            np.savetxt(filename,value,fmt='%.5f',delimiter=',')
            this_datatype = Datatype.query.filter_by(extension=extension).first()
            new_response = Response(assignment_id=self.id,student_id=student_id,datatype_id=this_datatype.id,var_name=var_name.lower())
            db.session.add(new_response)
            db.session.commit()

    def total_points(self):
        points = [question.max_grade for question in self.questions]
        return sum(points)

    def total_submissions(self):
        return len(self.submissions)

    def total_questions(self):
        return len(self.questions)

    def save_grades(self):
        assignment_grades_folder = os.path.join('grades',self.name)
        os.makedirs(assignment_grades_folder,exist_ok=True)
        assignment_feedback_folder = os.path.join('feedback',self.name)
        os.makedirs(assignment_feedback_folder,exist_ok=True)
        old_feedback = glob(os.path.join(assignment_feedback_folder,'*.txt'))
        for f in old_feedback:
            os.remove(f)

        q1 = BatchResponse.query.join('batch','question').options(db.joinedload('batch').joinedload('question'))
        q2 = q1.filter_by(assignment_id=self.id)
        q3 = q2.join('response','student').options(db.joinedload('response').joinedload('student'))

        df = pd.read_sql(q3.statement,db.engine)
        columns = ['student_id','grade','comments','name','status']
        df = df[columns]
        df.columns = ['Student ID','Grade','Comments','Question','Status']

        q4 = Submission.query.filter_by(assignment_id=self.id)
        submissions = pd.read_sql(q4.statement,db.engine)
        submissions = submissions[['student_id']]
        submissions.columns = ['Student ID']

        grades = df.pivot(index='Student ID',columns='Question',values='Grade').fillna(0)
        grades['Total'] = grades.sum(axis=1)

        grades = pd.merge(grades,submissions,left_index=True,right_on='Student ID',how='outer').fillna(0).set_index('Student ID')
        grades.to_csv(os.path.join(assignment_grades_folder,self.name) + '.csv')

        comments = df.pivot(index='Student ID',columns='Question',values='Comments').fillna('')
        comments = pd.merge(comments,submissions,left_index=True,right_on='Student ID',how='outer').fillna('').set_index('Student ID')

        statuses = df.pivot(index='Student ID',columns='Question',values='Status').fillna('Did not find a response for this question.')
        statuses = pd.merge(statuses,submissions,left_index=True,right_on='Student ID',how='outer').fillna('Did not find a response for this question.').set_index('Student ID')

        for student in grades.index:
            filename = os.path.join(assignment_feedback_folder,str(student) + '.txt')
            f = open(filename,'w')
            feedback = ''
            for question in comments.columns:
                comment = comments.loc[student,question]
                status = statuses.loc[student,question]
                grade = grades.loc[student,question]
                max_grade = Question.query.filter_by(assignment_id=self.id).filter_by(name=question).first().max_grade
                feedback += '\n{0}\nGrade: {1}/{2}\nStatus: {3}\nComments: {4}\n'.format(question,grade,float(max_grade),status,comment)
            f.write(feedback)
            f.close()


    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'total_points': self.total_points(),
                'total_questions': self.total_questions(),
                'total_submissions': self.total_submissions()}


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    var_name = db.Column(db.String(80), nullable=False)
    alt_var_name = db.Column(db.String(80), nullable=False)
    max_grade = db.Column(db.Integer, nullable=False)
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

    def delete_batches(self):
        for batch in self.batches:
            db.session.delete(batch)
        db.session.commit()

    def create_batches(self):
        if self.preprocessing:
            fun = self.get_preprocessing()
        else:
            fun = None
        submissions = Submission.query.filter_by(assignment_id=self.assignment_id)
        for submission in submissions:
            status = 'Response loaded successfully.'
            response = Response.query.filter_by(assignment_id=self.assignment_id,
                                                student_id=submission.student_id,
                                                var_name=self.var_name).first()

            if not response:
                alt_vars = self.alt_var_name.lower().split(',')
                for alt_var in alt_vars:
                    response = Response.query.filter_by(assignment_id=self.assignment_id,
                                                        student_id=submission.student_id,
                                                        var_name=alt_var).first()
                    if response:
                        status = 'Response loaded successfully. But variable name is misspelled!'
                        break

            if not response:
                continue

            batched = False
            for batch in self.batches:
                if batch.compare(response,preprocessing=fun):
                    this_batch = batch
                    batched = True
                    continue
            if not batched:
                this_batch = Batch(grade=0,comments='',datatype_id=response.datatype_id,question_id=self.id)
                db.session.add(this_batch)
                db.session.commit()
            batch_response = BatchResponse(response_id=response.id,batch_id=this_batch.id,status=status)
            db.session.add(batch_response)
            db.session.commit()

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


class BatchResponse(db.Model):
    response_id = db.Column(db.Integer, db.ForeignKey('response.id'), primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), primary_key=True)
    status = db.Column(db.String(140))

    response = db.relationship('Response', backref='batch_responses', lazy=True)

class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer)
    comments = db.Column(db.String(280))

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    datatype_id = db.Column(db.Integer, db.ForeignKey('datatype.id'), nullable=False)
    batch_responses = db.relationship('BatchResponse', backref='batch', lazy=True, cascade='all,delete')

    def compare(self,response,preprocessing=None):
        if self.datatype.id != response.datatype.id:
            return False
        response_data = response.get_data()
        batch_data = self.get_data()
        if preprocessing:
            try:
                response_data = preprocessing(response.student_id,response_data)
                batch_data = preprocessing(self.batch_responses[0].response.student_id,batch_data)
            except:
                print('Preprocessing failed ... ')
                pass
        dtype = self.datatype.name
        if dtype in ['text','symbolic']:
            return batch_data == response_data
        elif dtype == 'numeric':
            return np.array_equal(batch_data.shape,response_data.shape) and np.allclose(batch_data,response_data,atol=self.question.tolerance)
        elif dtype == 'figure':
            diffs = np.zeros([len(batch_data),len(response_data)])
            for sss in range(0, len(batch_data)):
                for aaa in range(0, len(response_data)):
                    if response_data[aaa].size > 2 and batch_data[sss].size > 2:
                        yinterp = np.interp(response_data[aaa][:,0], batch_data[sss][:,0], batch_data[sss][:,1]);
                        diffs[sss,aaa] = np.max(np.abs(yinterp-response_data[aaa][:,1]))
                    elif response_data[aaa].size == 2 and batch_data[sss].size == 2:
                        diffs[sss,aaa] = np.max(np.abs(response_data[aaa]-batch_data[sss]))
                    else:
                        diffs[sss,aaa] = 999
            diffs = diffs < self.question.tolerance
            if np.all(diffs.sum(axis=0)) and np.all(diffs.sum(axis=1)):
                return True
            else:
                return False
        else:
            return False

    def total_responses(self):
        return len(self.batch_responses)

    def get_fullfile(self):
        return self.batch_responses[0].response.get_fullfile()

    def get_data(self):
        return self.batch_responses[0].response.get_data()

    def to_dict(self):
        datatype = Datatype.query.get(self.datatype_id).name
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
                'data': dataJSON}

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    var_name = db.Column(db.String(80), nullable=False)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    datatype_id = db.Column(db.Integer, db.ForeignKey('datatype.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)

    def get_fullfile(self):
        return os.path.join('submissions',self.assignment.name,str(self.student_id),self.var_name + '.' + self.datatype.extension)

    def get_data(self):
        dtype = self.datatype.name
        filename = self.get_fullfile()
        if dtype == 'numeric':
            f = open(filename,'r')
            data = f.read()
            f.close()
            if 'i' in data:
                data = data.replace('i','j')
                dtype = complex
            else:
                dtype = float
            tmp = os.path.join('app','tmp.txt')
            file = open(tmp,'w')
            file.write(data)
            file.close()
            data = np.loadtxt(tmp,delimiter=',',ndmin=2,dtype=dtype)
            if data.size == 1:
                data = data.flat[0]
            os.remove(tmp)
        elif dtype == 'figure':
            f = open(filename,'r')
            data = f.read()
            f.close()
            data = json.loads(data)
            Lines = data['Lines']
            data = [np.array(Lines[n],dtype=float) for n in range(0,len(Lines))]
        else:
            f = open(filename)
            data = f.read()
            f.close()
        return data

class Datatype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    extension = db.Column(db.String(10), nullable=False)

    batches = db.relationship('Batch', backref='datatype', lazy=True)
    responses = db.relationship('Response', backref='datatype', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    responses = db.relationship('Response', backref='student', lazy=True)

class Submission(db.Model):
    grade = db.Column(db.Integer)
    feedback = db.Column(db.String(280))

    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    student = db.relationship('Student', backref='submissions', lazy=True)
