#!/usr/bin/env python

import pandas as pd
import numpy as np
from scipy.io.matlab import loadmat
import sys
import os
import argparse
from zipfile import is_zipfile, ZipFile
from enum import Enum

class FileTypes(Enum):
    ARRAY = '.csv'
    BOOL = '.log'
    STRING = '.txt'
    SYMBOL = '.sym'

def saveFile(path, var, ftype):
    with open(path, 'w') as f:
        if ftype is FileTypes.ARRAY or ftype is FileTypes.BOOL:
            np.savetxt(f, var, delimiter=',', comments='')
        else:
            print(path, ftype, var)
            f.write(var)

def makeFilename(var, dtype):
    var = var.lower()
    print('FileTypes', vars(FileTypes.ARRAY), FileTypes.ARRAY.value)
    if dtype in [np.uint8, np.int16, np.int32, np.float32, np.float64]:
        return FileTypes.ARRAY, var + FileTypes.ARRAY.value
    elif dtype in [np.dtype('bool')]:
        return FileTypes.BOOL, var + FileTypes.BOOL.value
    else:
        return FileTypes.STRING, var + FileTypes.STRING.value

def makeSubmission(sid, submission, dest, issues, ignore_vars):
    try:
        ml = loadmat(submission)
                
    except ValueError as ex:
        bad_fname = os.path.join(issues, sid.Submission)
        with open(bad_fname, 'wb') as f:
            extract = submission.read()
            f.write(extract)
        issues_fname = os.path.join(issues, 'issues.txt')
        with open(issues_fname, 'a') as f:
            f.write(ex.__repr__() + '\n')
        return

    directory = os.path.join(dest, str(sid.SID))
    try:
        os.makedirs(directory)
    except FileExistsError:
        pass
    for var in ml:
        if var not in ignore_vars:
            ftype, fname = makeFilename(var, ml[var].dtype)
            path = os.path.join(dest, str(sid.SID), fname)
            saveFile(path, ml[var], ftype)


def mapStudentIDs(id_file, sub_file):
    """Aggregates the canvas ids, student ids, and the names of the submitted files"""
    df = pd.read_csv(id_file, header = None, names = ['Canvas', 'SID'])
    df['Submission'] = ''
    for sub_name in sub_file.namelist():
        try:
            # Assumes no one has an underscore in their last name
            cid = int(sub_name.split('_')[1])
        except ValueError:
            # Handle late submissions
            try:
                cid = int(sub_name.split('_')[2])
            except ValueError as err:
                # Give up
                print(err)
                continue
        df.loc[df['Canvas'] == cid, 'Submission'] = sub_name
    print(df)
    return df

def main():
    parser = argparse.ArgumentParser(description = 'Parses student submissions to create the directory structure mbgrader expects')
    parser.add_argument('--submissions', action = 'store', default = 'submissions.zip', help = 'The file containing student submissions')
    parser.add_argument('--dest', action = 'store', default = 'canvas/hw', help = 'The directory to store student results')
    parser.add_argument('--id-file', dest = 'id_file', action = 'store', default = 'canvasIDstudentID.csv', help = 'The file containing canvas IDs and student IDs')
    parser.add_argument('--issues', dest = 'issues', action = 'store', default = 'issues/hw', help = 'The directory to store problematic student submissions')
    parser.add_argument('--ignore-vars', dest = 'ignore_vars', nargs = '+', action = 'store', default = [], help = 'Variables to ignore')
    args = parser.parse_args()
    if not os.path.isfile(args.submissions):
        print('Error: Could not find {}'.format(args.submissions))
        return
    if not is_zipfile(args.submissions):
        print('Error: {} is not a zip file of submissions'.format(args.submissions))
        return
    if not os.path.isfile(args.id_file):
        print('Error: Could not find {}'.format(args.id_file))
        return
    ignore_vars = args.ignore_vars + ['__header__', '__version__', '__globals__']
    f = ZipFile(args.submissions)
    sids = mapStudentIDs(args.id_file, f)
    try:
        os.makedirs(args.dest)
    except FileExistsError:
        pass
    try:
        os.makedirs(args.issues)
    except FileExistsError:
        pass
    for row in sids.itertuples():
        if row.Submission != '':
            with f.open(row.Submission) as submission:
                makeSubmission(row, submission, args.dest, args.issues, ignore_vars)

if __name__ == '__main__':
    main()
