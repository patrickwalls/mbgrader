from app import app, db
from app.models import Assignment, Question, Batch, Response, BatchResponse, Datatype, Student, Submission
from flask import render_template, jsonify, request, url_for, redirect

from .services.assignment import AssignmentService
from .services.question import QuestionService
from .services.grades import GradesService
from .services.batch import BatchService

from .selectors.assignment import get_all_assignments, get_assignment, get_assignment_vars
from .selectors.question import get_questions_of_assignment, get_question

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assignments', methods=['GET','POST'])
def assignments():
    if request.method == 'GET':
        assignments = get_all_assignments()
        return jsonify(assignments)

    elif request.method == 'POST':
        name = request.json["name"]
        folder_name = request.json["folder_name"]
        service = AssignmentService(
            name=name, folder_name=folder_name
        )
        new_assignment = service.create()
        service.load_submissions()

        return jsonify(new_assignment)

@app.route('/assignments/<int:assignment_id>', methods=['GET','DELETE'])
def assignment(assignment_id):
    if request.method == 'GET':
        assignment = get_assignment(assignment_id)
        return jsonify(assignment)

    if request.method == 'DELETE':
        service = AssignmentService(assignment_id=assignment_id)
        service.delete()
        return ('',204)

@app.route('/assignments/<int:assignment_id>/grades')
def grades(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    service = GradesService(
        assignment_id=assignment.id,
        assignment_name=assignment.name,
        root_folder=assignment.folder_name,
    )
    service.save()
    return ('',200)

@app.route('/assignments/<int:assignment_id>/vars')
def vars(assignment_id):
    vars_list = get_assignment_vars(assignment_id)
    return jsonify({'vars': vars_list})

@app.route('/assignments/<int:assignment_id>/questions', methods=['GET','POST'])
def questions(assignment_id):
    if request.method == 'GET':
        questions = get_questions_of_assignment(assignment_id)
        return jsonify(questions)
    elif request.method == 'POST':
        data = request.json
        service = QuestionService(
            name=data["name"],
            var_name=data["var_name"].lower(),
            alt_var_name=data["alt_var_name"].lower(),
            max_grade=data["max_grade"],
            tolerance=data["tolerance"],
            preprocessing=data["preprocessing"],
            assignment_id=assignment_id,
        )
        question = service.create()
        return jsonify(question)

@app.route('/assignments/<int:assignment_id>/questions/<int:question_id>', methods=['GET','DELETE'])
def question(assignment_id,question_id):
    if request.method == 'GET':
        question = get_question(question_id)
        return jsonify(question)
    if request.method == 'DELETE':
        service = QuestionService(question_id=question_id)
        service.delete()
        return ('',204)

@app.route('/assignments/<int:assignment_id>/response', methods=['POST'])
def create_response(assignment_id):
    var_name = request.form['name']
    vars = request.form['vars'].split(',')
    expression = request.form['expression']
    extension = request.form['extension']
    service = AssignmentService(assignment_id=assignment_id)
    service.create_responses(var_name, vars, expression, extension)
    return ('',200)

@app.route('/assignments/<int:assignment_id>/questions/<int:question_id>/batches', methods=['GET'])
def batch(assignment_id,question_id):
    create = request.args.get('create')
    if request.method == 'GET' and create == 'true':
        service = QuestionService(question_id=question_id)
        service.delete_batches()
        batches = service.create_batches()
        return jsonify(batches)
    elif request.method == 'GET' and create == 'false':
        question = Question.query.get_or_404(question_id)
        return jsonify([batch.to_dict() for batch in question.batches])

@app.route('/assignments/<int:assignment_id>/questions/<int:question_id>/batches/<int:batch_id>', methods=['GET','PUT'])
def grade(assignment_id,question_id,batch_id):
    if request.method == 'GET':
        batch = Batch.query.get_or_404(batch_id)
        return jsonify(batch.to_dict())
    elif request.method == 'PUT':
        data = request.json
        service = BatchService(
            batch_id=batch_id,
            grade=int(data["grade"]),
            comments=data["comments"]
        )
        graded_batch = service.grade()
        return jsonify(graded_batch)