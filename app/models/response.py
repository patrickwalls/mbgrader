from pathlib import Path
import numpy as np
from app import db


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    var_name = db.Column(db.String(80), nullable=False)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    datatype_id = db.Column(db.Integer, db.ForeignKey('datatype.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)

    def get_fullfile(self):
        submission_folder = Path("submissions/")
        assignment_folder = Assignment.query.get(self.assignment_id).folder_name
        student_folder = str(self.student_id)
        response_file = f"{self.var_name}.{self.datatype.extension}"
        return submission_folder / assignment_folder / student_folder / response_file

    def get_data(self):
        dtype = self.datatype.name
        filename = self.get_fullfile()
        if dtype in ['numeric','logical']:
            f = open(filename,'r')
            data = f.read()
            f.close()
            if 'i' in data:
                data = data.replace('i','j')
                dtype = complex
            else:
                dtype = float
            tmp = Path("app") / "tmp.txt"
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
