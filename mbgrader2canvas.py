import numpy as np
import pandas as pd
import os
import glob
from shutil import copyfile

assignment_name = input('Enter assignment name: ')
grades = pd.read_csv(os.path.join('grades',assignment_name + '.csv'))
classlist = pd.read_csv('classlist.csv',header=0,skiprows=[1,2])
columns = [c for c in classlist.columns if c in ['Student','ID','SIS User ID','SIS Login ID','Section','Student Number']]
classlist = classlist[columns]
total = grades[['Student ID','Total']]
upload = pd.merge(classlist,total,how='inner',left_on='Student Number',right_on='Student ID')
upload.drop(columns='Student ID',inplace=True)
upload.to_csv(os.path.join('grades',assignment_name + '_upload.csv'),index=False)

feedback_upload = os.path.join('feedback',assignment_name + '_upload')
os.makedirs(feedback_upload,exist_ok=True)
for old_file in glob.glob(os.path.join(feedback_upload,'*')):
    os.remove(old_file)

for i,row in classlist.iterrows():
    studentID = row['Student Number']
    if np.isnan(studentID):
        continue
    source = os.path.join('feedback',assignment_name,str(int(studentID)) + '.txt')
    if not os.path.isfile(source):
        continue
    canvasID = row['ID']
    submission = glob.glob(os.path.join('canvas',assignment_name,'*_{}_*.mat'.format(canvasID)))
    if not submission:
        submission = glob.glob(os.path.join('canvas',assignment_name,'*_{}_*.fig'.format(canvasID)))
    if not submission:
        continue
    destination = os.path.join(feedback_upload,os.path.basename(submission[0]))
    copyfile(source,destination)
