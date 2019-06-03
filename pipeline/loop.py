import pandas as pd
import numpy as np

from sklearn.model_selection import ParameterGrid

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import BaggingClassifier

from sklearn.linear_model import LinearRegression
from sklearn.svm import LinearSVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from .evaluate import ClassifierEvaluator, RegressionEvaluator


seed = 1234
clfs = {'LR':  LogisticRegression(solver='liblinear', random_state=seed),
        'KNN': KNeighborsClassifier(),
        'DT':  DecisionTreeClassifier(random_state=seed),
        'SVM': SVC(kernel='linear', probability=True, random_state=seed),
        'RF':  RandomForestClassifier(random_state=seed),
        'GB':  GradientBoostingClassifier(random_state=seed),
        'AB':  AdaBoostClassifier(random_state=seed),
        'NB':  GaussianNB(),
        'ET':  ExtraTreesClassifier(random_state=seed),
        'BC':  BaggingClassifier(random_state=seed, bootstrap=True)}

clf_small_grid = {'LR':  {'penalty': ['l1','l2'], 'C': [0.01,0.1]},
                  'KNN': {'n_neighbors': [5,10],'weights': ['uniform','distance'],'algorithm': ['auto','ball_tree','kd_tree']},
                  'DT':  {'criterion': ['gini', 'entropy'], 'max_depth': [5,50], 'max_features': [None],'min_samples_split': [5,10]},
                  'SVM': {'C': [0.01,0.1]},
                  'RF':  {'n_estimators': [100,1000], 'max_depth': [5,50], 'max_features': ['sqrt','log2'],'min_samples_split': [5,10]},
                  'GB':  {'n_estimators': [100,1000], 'learning_rate' : [0.01,0.05],'subsample' : [0.1,0.5], 'max_depth': [5,10]},
                  'AB':  {'algorithm': ['SAMME', 'SAMME.R'], 'n_estimators': [100,1000]},
                  'NB':  {},
                  'ET':  {'n_estimators': [100,1000], 'criterion' : ['gini', 'entropy'] ,'max_depth': [5,10], 'max_features': ['sqrt','log2'],'min_samples_split': [5,10]},
                  'BC':  {'n_estimators': [100,1000]}}

clf_large_grid = {'LR':  {'penalty': ['l1','l2'], 'C': [0.00001,0.0001,0.001,0.01,0.1,1,10]},
                  'KNN': {'n_neighbors': [1,5,10,25,50,100],'weights': ['uniform','distance'],'algorithm': ['auto','ball_tree','kd_tree']},
                  'DT':  {'criterion': ['gini', 'entropy'], 'max_depth': [1,5,10,20,50,100], 'max_features': [None],'min_samples_split': [2,5,10]},
                  'SVM': {'C' :[0.00001,0.0001,0.001,0.01,0.1,1,10]},
                  'RF':  {'n_estimators': [1,10,100,1000,10000], 'max_depth': [1,5,10,20,50,100], 'max_features': ['sqrt','log2'],'min_samples_split': [2,5,10]},
                  'GB':  {'n_estimators': [1,10,100,1000,10000], 'learning_rate' : [0.001,0.01,0.05,0.1,0.5],'subsample' : [0.1,0.5,1.0], 'max_depth': [1,3,5,10,20,50,100]},
                  'AB':  {'algorithm': ['SAMME', 'SAMME.R'], 'n_estimators': [1,10,100,1000,10000]},
                  'NB':  {},
                  'ET':  {'n_estimators': [1,10,100,1000,10000], 'criterion' : ['gini', 'entropy'] ,'max_depth': [1,5,10,20,50,100], 'max_features': ['sqrt','log2'],'min_samples_split': [2,5,10]},
                  'BC':  {'n_estimators': [1,10,100,1000,10000]}}

regs = {'LR': LinearRegression(),
        'SVR': LinearSVR(),
        'DTR': DecisionTreeRegressor(),
        'RFR': RandomForestRegressor()}

reg_small_grid = {'LR': {},
                  'SVR': {'C' :[0.01,0.1]},
                  'DTR': {'max_depth': [5,50], 'max_features': [None],'min_samples_split': [2,5,10]},
                  'RFR': {'n_estimators': [100,1000], 'max_depth': [5,50], 'max_features': ['sqrt','log2'],'min_samples_split': [2,5,10]}}

reg_large_grid = {'LR': {},
                  'SVR': {'C' :[0.00001,0.0001,0.001,0.01,0.1,1,10]},
                  'DTR': {'max_depth': [1,5,10,20,50,100], 'max_features': [None],'min_samples_split': [2,5,10]},
                  'RFR': {'n_estimators': [1,10,100,1000,10000], 'max_depth': [1,5,10,20,50,100], 'max_features': ['sqrt','log2'],'min_samples_split': [2,5,10]}}


def run_clf_loop(test_df, train_df, clfs, grid, label_col, thresholds):
    '''
    thresholds between 0 and 100
    '''
    X_train = train_df.drop(columns=[label_col])
    X_test = test_df.drop(columns=[label_col])
    y_train = train_df[label_col]
    y_test = test_df[label_col]

    evaluation_table = []
    col_names = ['classifier', 'parameters', 'threshold'] + ClassifierEvaluator.metric_names()

    for c, model in clfs.items():
        parameter_values = grid[c]

        for p in ParameterGrid(parameter_values):
            model.set_params(**p)
            model.fit(X_train, y_train)
            scores = model.predict_proba(X_test)[:,1]

            for t in thresholds:
                evaluator = ClassifierEvaluator(scores, y_test, t)
                evaluation_table.append([c, p, t] + evaluator.all_metrics())

    return pd.DataFrame(evaluation_table, columns=col_names)


def run_reg_loop(test_df, train_df, regs, grid, label_col):
    '''
    '''
    X_train = train_df.drop(columns=[label_col])
    X_test = test_df.drop(columns=[label_col])
    y_train = train_df[label_col]
    y_test = test_df[label_col]

    evaluation_table = []
    col_names = ['classifier', 'parameters'] + RegressionEvaluator.metric_names()

    for r, model in regs.items():
        parameter_values = grid[r]

        for p in ParameterGrid(parameter_values):
            model.set_params(**p)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            evaluator = RegressionEvaluator(y_pred, y_test)
            evaluation_table.append([r, p] + evaluator.all_metrics())

    return pd.DataFrame(evaluation_table, columns=col_names)











