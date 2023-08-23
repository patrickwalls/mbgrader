from pathlib import Path
import pandas as pd
from app import app, db
from ..models import BatchResponse, Submission


class GradesService:
    def __init__(
        self,
        *,
        assignment_id: int = None,
        assignment_name: str = None,
        root_folder: Path = None,
    ):
        self.assignment_id = assignment_id,
        self.assignment_name = assignment_name
        self.root_folder = root_folder

    def save(self):
        grades_folder = Path("grades")
        grades_folder.mkdir(exist_ok=True)

        feedback_folder = Path("feedback")
        feedback_folder.mkdir(exist_ok=True)
        assignment_feedback_folder = feedback_folder / self.assignment_name
        assignment_feedback_folder.mkdir(exist_ok=True)

        old_feedback = assignment_feedback_folder.glob("*.txt")
        for f in old_feedback:
            f.unlink()

        q1 = BatchResponse.query.join('batch','question').options(db.joinedload('batch').joinedload('question'))
        q2 = q1.filter_by(assignment_id=self.assignment_id)
        q3 = q2.join('response','student').options(db.joinedload('response').joinedload('student'))

        df = pd.read_sql(q3.statement,db.engine)
        columns = ['student_id','grade','comments','name','status']
        df = df[columns]
        df.columns = ['Student ID','Grade','Comments','Question','Status']

        q4 = Submission.query.filter_by(assignment_id=self.assignment_id)
        submissions = pd.read_sql(q4.statement,db.engine)
        submissions = submissions[['student_id']]
        submissions.columns = ['Student ID']

        grades = df.pivot(index='Student ID',columns='Question',values='Grade').fillna(0)
        grades['Total'] = grades.sum(axis=1)

        grades = pd.merge(grades,submissions,left_index=True,right_on='Student ID',how='outer').fillna(0).set_index('Student ID')
        grades.to_csv(os.path.join(grades_folder,self.root_folder) + '.csv')

        comments = df.pivot(index='Student ID',columns='Question',values='Comments').fillna('')
        comments = pd.merge(comments,submissions,left_index=True,right_on='Student ID',how='outer').fillna('').set_index('Student ID')

        statuses = df.pivot(index='Student ID',columns='Question',values='Status').fillna('Did not find a response for this question.')
        statuses = pd.merge(statuses,submissions,left_index=True,right_on='Student ID',how='outer').fillna('Did not find a response for this question.').set_index('Student ID')

        for student in grades.index:
            filename = assignment_feedback_folder / f"{student}.txt"
            f = open(filename,'w')
            feedback = '{}\nStudent ID: {}\n'.format(self.assignment_name,student)
            for question in comments.columns:
                comment = comments.loc[student,question]
                status = statuses.loc[student,question]
                grade = grades.loc[student,question]
                max_grade = Question.query.filter_by(assignment_id=self.assignment_id).filter_by(name=question).first().max_grade
                feedback += '\n{0}\nGrade: {1}/{2}\nStatus: {3}\nComments: {4}\n'.format(question,grade,float(max_grade),status,comment)
            f.write(feedback)
            f.close()
