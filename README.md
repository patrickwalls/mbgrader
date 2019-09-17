# mbgrader

mbgrader (**m**ath **b**atch **grader**) is a custom web application for batch grading MATLAB assignments.

## Requirements

```
flask=1.1.1
flask-sqlalchemy=2.4.0
numpy=1.16.4
pandas=0.25.1
python=3.7.4
sqlalchemy=1.3.7
sqlite=3.29.0
```

## Quickstart

Setup the database:

```
python init_db.py
```

Setup the Flask environment variable and run:

```
export FLASK_APP=app
flask run
```

Open a browser and navigate to `http://127.0.0.1:5000/`. Create a new assignment by entering the corresponding folder name locating in the `submissions` folder. There is an example assignment called `example1`. mbgrader assumes the folder structure:

```
submissions/
    assignment_name/
        student_id_1/
            var1.csv
            var2.csv
            var3.txt
        student_id_2/
            var1.csv
            var2.csv
            var3.txt
```

Create a new question and enter a preprocessing function if necessary.
