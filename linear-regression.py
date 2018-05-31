#!/usr/bin/env python3

import sys 
import time
 
from random import randint

import pandas as pd
from sklearn import cross_validation
from sklearn.linear_model import LinearRegression

#  read dataset as the 1st command line argument
dataset = sys.argv[1]

#load dataset
df = pd.read_csv("/work/"+dataset)

#prepare splits for 10 fold cross validation
kf_total = cross_validation.KFold(len(df), n_folds=10,  shuffle=True, random_state=4)

# get x data .. only features, no target variable
x = df.iloc[:,:-1]

# this is the target variable
y = df.iloc[:,-1]

# create a Linear Regression object
lreg = LinearRegression()
# now apply 10 fold cross validaton and get array of scores
scores = cross_validation.cross_val_score(lreg, x, y, cv=kf_total, n_jobs = 1)
# compute avg score
score = sum(scores)/scores.size

with open("/work/"+dataset+".out", "a") as text_file:
    text_file.write(str(score))
