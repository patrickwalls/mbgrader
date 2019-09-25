# mbgrader

mbgrader (**m**ath **b**atch **grader**) is a custom web application for batch grading assignments where students submit numbers and matrices as `.csv` files, or text in `.txt` files.

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

Create a new question and enter a preprocessing function if necessary. Requirements for the preprocessing function are:

* Function must be named `fun`.
* Input parameters:
  * `s` is the student number: `int`
  * `r` is the response: `str`, `np.float64`, or `np.ndarray`
* Return value *must* be the same type as the response.

For example, the preprocessing function for the question "What is your student number?":

```python
import numpy as np

def fun(s,r):
    if isinstance(r,str):
        return "text"
    elif isinstance(r,np.ndarray):
        return np.array([0,0])
    else:
        if abs(r - s) > 0:
            return np.float64(1)
        else:
            return np.float64(0)
```
