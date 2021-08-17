#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 15:12:01 2018

@author: al2myers

Reformats the student report from Canvas to "long form" for easier analysis and
ability to compare multiple quizzes. Reads all csv data in a particular folder, 
and where possible outputs the data with the original name + _long_format". 

"""
import os
import pandas as pd
import re
import sys

### reformat Student Report from Canvas
# questions need to take the form of "idnumber: anything" ie. "223232: some question"

question_re = re.compile("(\d)*(\:){1}")

""" when read in as columns points will add a numeric indicator of order i.e. if 
there are 2 "1.0" they would become 1.0 and 1.0.1 """

points_re = re.compile("(\d)*\.(\d)*$|(\d)*$|(\d)*\.(\d)*\.(\d)*$")
pointspossible_re = re.compile("(\d)*\.(\d)*$|(\d)*$")

id_cols = ["name", "id", "sis_id", "section", "section_id", "section_sis_id", "submitted", "attempt"]
summary_cols = ["n correct", "n incorrect", "score"]

    
def parse_question_id(string):
    out = question_re.search(string).group()
    questionid_re = re.compile("(\d)*")
    out = questionid_re.search(out).group()
    return(out)
    
def zigzag(seq):
  return seq[::2], seq[1::2]

class Error(Exception):
   """Base class for other exceptions"""
   pass

# Create some errors based on the expected data format
class DataFrameEmptyError(Error):
    """Raised when the dataframe has no rows"""
    pass

class ColumnsError(Error):
    """Raised when the dataframe is missing the ID columns needed or doesn't have 
    the correct question_id and points columns
    """
    pass
    
    
def create_long_df(folder, file):
    
    print("\n Attempting to create output for {}".format(file))
    df = pd.read_csv("{}/{}".format(folder, file), header=None, nrows=1)
    column_original = df.iloc[0]
    ### does this contain 
    df = pd.read_csv("{}/{}".format(folder, file))
    
    
    # make sure the dataframe is not empty
    try:
        is_empty = df.shape[0] == 0
        if is_empty == True:
            raise DataFrameEmptyError
    except DataFrameEmptyError:
        print("FAIL: the dataframe had no rows of data")
        pass
    else:
          
        remove_cols = id_cols + summary_cols
        
        # make sure the remove_cols all exist (these are IDs and summaries)
        try:
            if not(set(remove_cols).issubset(column_original)):
                raise ColumnsError
        except ColumnsError:
            print("FAIL: the dataframe is missing the defined id columns")
            pass
        else:
                
            new_list = [name for name in column_original if name not in remove_cols]
            questions, points_possible = zigzag(new_list)
        
        
            # make sure that questions and points possible follow the correct formats
            try: 
                if not(all([question_re.match(q) for q in questions]) & all([pointspossible_re.match(str(p)) for p in points_possible])):
                    raise ColumnsError
            except ColumnsError:
                print("FAIL: something wrong with question/point columns")
                pass
            else:
        
                question_cols = list(filter(question_re.match, df.columns))
                questions_df = df[id_cols + question_cols]
                
                points_cols = list(filter(points_re.match, df.columns))
                points_df = df[id_cols + points_cols]
                
                question_score_pairs = pd.DataFrame({'question':questions, 
                                                     'possible_points':points_possible,
                                                     'points_id': points_cols})
                
                
                
                question_score_pairs['question_id'] = question_score_pairs['question'].apply(lambda x: parse_question_id(x))
                
                questions_long = pd.melt(questions_df, id_vars=id_cols, var_name="question", value_name="response")
                points_long = pd.melt(points_df, id_vars=id_cols, var_name="points_id", value_name="points_given")
                
                final_df = pd.merge(questions_long, question_score_pairs, how='left', 
                                    on=['question'])
                final_df = pd.merge(final_df, points_long, how='left',
                                    on=id_cols + ['points_id'])
                
                file_out = file.replace(".csv", "")
                
                final_df['file_name'] = file_out
                
                outname = "{}/{}_long_format.csv".format(folder, file_out)
                final_df.to_csv(outname)
                
                print("SUCCESS: {} created".format(outname))

                return(final_df)

def main():
    folder = 'quiz_student_analysis_file'
        
    files = os.listdir(folder)
    files = [file for file in files if re.search(".csv", file)]
    print(files)
    
    #don't try this for long formats already
    files = [file for file in files if not re.search("_long_format.csv", file)]
    
    if files==[]:
        print(f"No files in {folder}, please add your export and run again")
        sys.exit()

    for file in files:
        try:
            create_long_df(folder, file)
        except:
            print("ERROR: something unknown happened")


if __name__ == '__main__':
    main()
    
    
    
