# Step-by-step Guide for *mbgrader*

## Introduction

This guide is intended to help installing and using *mbgrader*, a custom web application for batch grading assignments. Visit [here](https://github.com/patrickwalls/mbgrader) for more information about the software.

## Installation

Clone the git repositiory:

    git clone https://github.com/patrickwalls/mbgrader.git

See `pyproject.toml` for required Python packages. Or create a virtual environment using pip:

    python -m venv env
	source env/bin/activate
    pip install --editable .

Initialize the SQLite database:

    flask init-db

4. Note you only need to run `flask init-db` once for all. Running it a second time will erase previous grading records. Then the *mbgrader* is all set.

## Preparing Assignments

### Create files for the course:

1. **classlist.csv**:
	2.  Navigate to the `Canvas Course Page`, then go to `Grade`. Click `Action`-`Export` to get the full classlist (it may take a few seconds to start). 
	3. Then a `.csv` file will be downloaded to your local drive. Change the file name to **`classlist.csv`** and put it under the `./mbgrader/` folder. 
4. **canvasIDstudentID.csv**:
	5. After getting the `classlist.csv`, duplicate it and open the new file in Excel. 
	6. Among all the columns, **move the `ID` (this is the canvas ID) to the first column and the `Student ID` to the second column**, delete the remaining columns. 
	7. Save the file as **`canvasIDstudentID.csv`** and put it under the `./mbgrader/` folder. 

**Note:** 
_1._ these two steps are new, please make contact if there is any problem.
_2._ The above steps should be repeatedly done for each assignment before the add-drop deadline in case there are changes of enrollment. 

****
### Convert submission to *mbgrader*-ready files

1. Under the `./mbgrader` directory, create a directory called `canvas`.

		(base) $ mkdir ./mbgrader/canvas
	
2. Download the target assignments from the Canvas. The assignments are usually compressed,
3. Unzip the compressed assignments, put the unzipped folder under `./mbgrader/canvas/` with suitable name. For this guide, the assignment folder is assumed to call `assignment_sample`.
5. Open the `canvas2mbgrader.m` file in MATLAB, and run the script. Serveral inputs will be required:
	* `Enter assignment folder [canvas/{*}]`: 
	enter the name of the assignment directory to be graded. In this guide, the input should be `assignment_sample`
	
	* `Enter variable names to ignore`: (**optional**) large size of irrelevant matrices commonly shared in students' submission (e.g. data file provided to complete the assignment) could slow down the processing. Identify those variable names and input here to ignore them during the processing. *Don't input the variables to be graded*
	* `Enter preferred variable names`: (**optional**) The script will extract students' responses and save them to a new file, but there is no difference between upper and lower case. For example, variables Y and y will both save to y.csv. The preferred name would indicate which variable to save either Y or y.
	* The complete display in MATLAB shoud look like this: 

			>> canvas2mbgrader
			Found _(number)_ students in the classlist.
			Enter assignment folder [canvas/{*}]: assignment_sample
			Enter variable names to ignore (as comma-separated list with no spaces such as ans,varA,varB): 
			Enter preferred variable names (as comma-separated list with no spaces such as X,Y,Z): 
			
6. A new directory with the name being the target assignment folder will be created under the directory `./mbgrader/submission/`, i.e. `./mbgrader/submissions/assignment_sample/`, containing reorganized and extracted students' responses ready for the *mbgrader*. 

	_Example_: The result will be a new file called OneCcode\_eval.csv for each student's response variable 'OneCcode' (and OneCcode_eval.txt with text “Command did not execute.” for those responses which could not be evaluated properly).
	
****
### Problematic Submission	
1. Another directory with the name being the target assignment folder will be created under the directory `./mbgrader/issue/`. This directory contains all the students submission that cannot be processed properly. The `./issue/issues.txt` file lists corresponding reasons.
2. _Wrong Submission_
	2. **Download the assignment immediately at the due date and then run canvas2mbgrader.m to get this `issues.txt` file.** Identify submission with reason being: 'Could not open .mat file', then contact the students for resubmission, and let them know the resubmission policy (should discuss with your IIC).
		* For example: a -X% late submission deduction, and not accepting submissions after Y days. 
	3. Then you note down those student IDs and can start grading after that Y-day. In this way, we can effectively reduce the number of wrong submissions and student complaints. 

4. _Multiple Submission_: Multiple submission would not be moved into the issue folder, unlike the wrong submissions. And it would only cause a problem if students accidentally submit two `.mat` files at once where one contains reasonable answers while the other contains nonsense but with the same variable name (very unlikely) so the `mbgrader` will overwrite those variables. Just take a quick look at those multiple `.mat` submissions (find them by their Canvas ID in `./canvas/(assignment_name)/`), and take out the extra `.mat` file if it's really a wrong submission.



## Grading
### Tips before grading
1. Usually there won't be solution sheet provided. You should go through the questions on your own, find the correct way as well as **possible wrong ways** in order to identify **'reasonable' wrong answers** when grading (e.g. typos, messing up variables etc.) so that proper comments can be given to partial-credit answers.
2. You **should** mark the correct solution as well as the wrong solutions down, along with explanations and corresponding scores on your own rubric. It would be very useful in many ways. 
3. The following process looks long since it covers everything in a detailed manner, but it's recommended to fully go through them once to understand what each part is about.

****
### Normal Process

1. Open terminal in the `./mbgrader/` folder, and enter the following command:

		(env) $ flask run  #(or python/python3 -m flask run)

2. You are expected to see output below meaning the application is launched. 

 		 * Serving Flask app "app"
		 * Environment: production
		   WARNING: This is a development server. Do not use it in a production deployment.
		   Use a production WSGI server instead.
		 * Debug mode: off
		 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

3. Leave the terminal running. Copy the url from the last line and open it in your browser.
4. You will be directed to the *_assignment page_* of *mbgrader*. Click `New Assignment` and input the assignment name you are about to grade. **The input name should be exactly the same as the local directory name under `./submission/` in order to load the assignments properly**. In this guide, the input should be 'assignment_sample'.

5. Then, the newly created assignment should appear in the *_assignment page_*, showing the name of the assignment, number of submissions, etc. Click `Grade`to enter the *_question page_* of the corresponding assignment.

6. In the *_question page_*, there are four buttons: `New Question`, `Save Grades`, `Find Variables` and `Create Reposne`.
	* `New Question`: Click the button to create a new *_grading page_* for a question/variable. You will see a 'Create Question' interface after clicking. **Note that for each *grading page*/'Create Question', only one variable can be graded.** For example, in question 1, there are two variables to grade, but you should treat them as two separate questions and grade those two variables separately. 

		* **Question Name**: Design a question name **specified for the variable** to be graded. For example, if we are grading the first variable of question 1, we can name the question as 'Q1a'. You should name it properly as students will use this name to read the breakdown of their marks.
		* **Variable Name**: Enter the variable name submitted by students. These names should match with the variable names from the student submission for the program to read. You can use the `Find Variables` function to search for variable names.
		* **Other Variable Names**: Some students might have typos when creating their variable names. Though it's their responsibilities to make sure the names are correct, we still try to minimize their loss (otherwise they complain). So here, input the variable names with typos with comma separated so those variables can still be read. You can use the `Find Variables` function to search for variable names.
		* **Maximum Grade**: Enter the full mark for the variable/question determined by you. For each variable normally it ranges from 1 to 3. You should create your own rubric, and decide based on diffculty of the questions and potential hierachy of student responses.
		* **Tolerance**: Set up the round-off precision, usually 0.001 or 0.0001 is enough.
		* **def fun(s,r)**: this is the *preprocessing function*, it's a big topic to be dicussed later. 
	* `Save Grades`: This is for saving the final grades after finishing the grading.
		* You could also use it for checkpoint saving but normally there is no need: the *mbgrader* can't read back the saved grades, and there is a auto-cache: even you quit the process in terminal and reopen it, you can still have your previous graded questions.
	* `Find Variables`: By clikcing this button, a full list of every distinct variable names from all student submissions will show up.
	* `Create Response`: This function is useful when you need to create a variable based on several responses to check. This is different from the *preprocessing function* where only one variable can be read. This function can combine different variables. Here's an example:
		*  The question asks students to submit two variables A and B where A+B is a constant. 
		*  In the 'Create Response' interface, the 'Response Variable Name' is the new variable name you are creating to check if A+B is a constant. We call it C here. So input `C`.
		*  In the second row, input the variable names you need to include to create such new response in brackets with comma-separated. Here we input `(A, B)`. 
		*  Now we need to write an expression in the thrid row to compute the new variable `C`. The input should be an anonymous function `lambda v: (function content)` exactly as the format shown, where 'v' is the input list we had from the second row. In our example, `v = [A,B], v[0]=A, v[1] = B`, input `lambda v: v[0]+v[1]`. 
		*  Lastly, specify the format of the new variable. Since we are checking the numerical value of C, we should input `'csv'`.
		*  After creating the new variable, we are supposed to locate it in `Find Variables`, hence can use it as a new variable to start a new question.
	
* After creating a new question, it should show up in the *_question page_*. Click the `Batch!` button on the right to batch students' responses. And then click `Grade` to proceed to grading. 
* Then you will be directed to the *_pre-grading page_* where you can see status of each batched response. There are some important attributes to look at:
	* **Count**: The 'Count' shows you the number of students response associated to that batch. The majority should likely to be correct (hopefully).
	* **Total number of batches**: You can simply count or look at the 'Batch ID'. If the number of batches is excessively high, say 50, meaning 50 different responses are to be graded in total, you probably shouldn't grade it directly. You should consider writing a *preprocessing function* (**def fun(s,r)** above) to reduce the variance.
* Click 'Grade' on the right to grade each batch. Then you will enter the *_grading page_*, where you see batched responses along with attributes of them. Assign grade and write comments below to the batch. **Then click `Submit` to store the current grade and comments**. Then click `Next` to proceed to the next one.
	* Sometimes after clicking `Next`, it won't proceed to the next. Just go back to the upper level through the navigation on top left and re-enter the _grading page_, and it should be fine from there. 
	* You might also want to check the 'Datatype' of the response. 
	* Comments are reusable accross different questions and even different assignments! They will be shown in the dropdown menu once you click in 'Comments'.

****

### After Grading
* **Save grades and comments**: Click `Save Grades` in the *_question page_* to save grades and comments to your local drive. Folders corresponding to 'Grades' and 'Comments' will be created under `./mbgrader/grades/` and `./mbgrader/feedback/` respectively with names asscoiated to the assignment.
* **Convert grades and comments**: Run the `mbgrader2canvas.py` using python to convert feedback and grades to Canvas-ready format. After that you should see `./mbgrader/grades/(assignment name)_upload.csv` and `./mbgrader/feedback/(assignment name)_upload/` created.
* **Upload grades and comments**:
	* Grades: On Canvas, navigate to the `Course Page-Grade`, under the `Action` tab, select `import`. Then, import the `./grades/(assignment name)_upload.csv` file. 
	* Comments: Navigate to the `Course Page-Assignment-(Current Assignment)`, then click the `resubmission` on the right under `Download Submissions`, submit the folder `./feedback/(assignment name)_upload/`. 
* **The issue submissions**: Adjust the grade mannually on Canvas according to the previous record for issue submissions.

**** 
### Preprocessing Function
The preprocessing function **def fun(s,r)** is an option to preprocess students response when creatnig a new question. Many times, it helps reduce the number of batches, that is the number of different answers, to be graded.

The preprocessing function should be written in Python, following all the formatting (indent, syntax, package, etc.), with input variable `s` being the student number and `r` being the student response. **It's highly recommended that you write the script in some other python interpreters**, test it, then copy and paste it into the `mbgrader` function box.

Note that the output variable datatype of the preprocessing function should match exactly with the input (student response) datatype: if the student response is a `string`, the output variable should also be a `string`. The input datatypes are usaually: `string`, `float` and `numpy.ndarray`. 

Besides, if you want to define a matrix for preprocessing usage, **you need to write it inside the preprocessing function** `def fun(s,r)`.

Two examples of prerpocessing function are shown below:

1. Match response with student ID:
	
		import numpy as np
		def fun(s,r):
		    if isinstance(r,str):
		        return "text" # so the response will show as 'text'
		    elif isinstance(r,np.ndarray):
		        return np.array([0,0])  # so you know student submit an array
		    else:
		        if abs(r - s) > 0: 
		            return np.float64(1)
		        else:
		            return np.float64(0)
	
2. Thresholding student response: 
	
		import numpy as np
		def fun(s,r):
		    if isinstance(r,float): 
		        if abs(r - 1) < 0.1: # thresholding at 1, correct answer
		            return np.float64(2)
		        elif abs(r-1) < 5: # in a reasonable range but not so correct
		            return np.float64(1)
		        else:
		            return np.float64(0)
		    else:
		        return r # do nohting then it returns the original response


You want to write preprocessing functions that can successfully minimize the batch numbers while also being able to separate different levels of responses. 

**_Error Shooting_:** Preprocessing function could fail in two ways:

1. Not batching the responses: it's usually because it fails to satisfy the `if-condition`, you need to debug your script and start a new question.

2. Taking forever to proocess/not responding: then it's likely that your script could not run properly by python, go to the *mbgrader* terminal and debug according to the error message. Use `ctrl+c`, or whatever keys combination, to terminate the *mbgrader* program and restart itt again. 