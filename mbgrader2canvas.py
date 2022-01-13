from canvasapi import Canvas
import glob
import tempfile
import os

API_URL = "https://ubc.instructure.com"
with open("token.txt","r") as f:
    API_KEY = f.read()
canvas = Canvas(API_URL, API_KEY)

courseID = int(input("Enter Canvas course ID: "))
assignmentID = int(input("Enter Canvas assignment ID: "))
course = canvas.get_course(courseID)
assignment = course.get_assignment(assignmentID)
assignment_name = input("Enter assignment name: ")

with open("canvasIDstudentID.csv") as f:
    lines = f.readlines()

studentIDcanvasID = {}
for line in lines:
    items = line.split(",")
    canvasID = int(items[0])
    studentID = int(items[1])
    studentIDcanvasID[studentID] = canvasID

with open(os.path.join("grades",assignment_name + ".csv")) as f:
    lines = f.readlines()

for line in lines[1:]:
    items = line.split(',')
    student_id = int(items[0])
    canvas_id = studentIDcanvasID[student_id]
    try:
        submission = assignment.get_submission(canvas_id)
    except:
        print('Could not find assignment for {}'.format(canvas_id))
        continue
    score = float(items[-1])
    print("Upload grade {} for {} ...".format(score,canvas_id))
    submission.edit(submission={'posted_grade': score})
    print("Upload feedback for {} ...".format(canvas_id))
    f = tempfile.NamedTemporaryFile('w+')
    f.name = "feedback.txt"
    source = os.path.join("feedback",assignment_name,"{}.txt".format(student_id))
    with open(source,'r') as fsource:
        f.write(fsource.read())
    f.seek(0)
    submission.upload_comment(f)
    f.close()
