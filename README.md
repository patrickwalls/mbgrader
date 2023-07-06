# mbgrader

mbgrader (**m**ath **b**atch **grader**) is a custom web application for batch grading assignments where students submit numbers and matrices as `.csv` files, or text in `.txt` files.

## Quickstart

Clone the repository:

    git clone https://github.com/patrickwalls/mbgrader.git
    cd mbgrader

Setup environment:

    python -m venv env
    source env/bin/activate
    pip install --editable .

Initialize the database:

    flask init-db

Run the development server:

    flask run

Open a browser and navigate to `http://127.0.0.1:5000/`. Create a new assignment by entering the corresponding folder name locating in the `submissions` folder. There is an example assignment called `example1`. mbgrader assumes the folder structure:

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

See the [documentation](docs/guide.md) for more information.

## Canvas LMS API Integration

The Jupyter notebook `canvas2mbgrader.ipynb` provides Canvas LMS API integration for mbgrader:

* Connect to Canvas LMS API
* Download student submissions
* Read student .mat and .fig files into mbgrader
* Upload mbgrader grades and feedback to Canvas