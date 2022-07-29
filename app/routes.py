from app import app, db
from app.models import Assignment, Question, Batch, Response, BatchResponse, Datatype, Student, Submission
from flask import render_template, jsonify, request, url_for, redirect

@app.route('/')
def index():
    return render_template('index.html')

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
