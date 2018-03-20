#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi','total_stock_value','exercised_stock_options',
                'bonus','deferred_income','salary','expenses','total_payments',
                 'restricted_stock','long_term_incentive','shared_receipt_with_poi','other',
                 'from_poi_to_this_person','poi_message_percentage']
# You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
data_dict.pop( 'TOTAL', 0 )
data_dict.pop( 'LOCKHART EUGENE E', 0 )
data_dict.pop( 'THE TRAVEL AGENCY IN THE PARK', 0 )

print 'After removing outliers, new number of data point is {0}'.format(len(data_dict))
### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.
my_dataset = data_dict

for k,v in my_dataset.iteritems():
    to_messages = v['to_messages'] 
    from_poi_to_this_person = v['from_poi_to_this_person']
    from_messages = v['from_messages']
    from_this_person_to_poi = v['from_this_person_to_poi']

    if to_messages == 'NaN' or from_poi_to_this_person == 'NaN' or from_messages == 'NaN' or from_this_person_to_poi == 'NaN':
        v['poi_message_percentage'] = 'NaN'
    else:
        poi_message_percentage = 1.0*(from_poi_to_this_person+from_this_person_to_poi/(from_messages+to_messages))
        v['poi_message_percentage'] = poi_message_percentage

    ### Deal with error input
    if k=='BHATNAGAR SANJAY':
        v['restricted_stock'] = abs(v['restricted_stock'])

    if k=='BELFER ROBERT':
        v['total_stock_value'] = abs(v['total_stock_value'])

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.

####################################
# Params Selection Prepare
####################################
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

clf_NB = GaussianNB()
param_NB = dict(reduce_dim__n_components=[2,3,4])

clf_DT = DecisionTreeClassifier()
param_DT = dict(reduce_dim__n_components=[2,3,4], clf__min_samples_split=[20, 40, 80, 100])

clf_SVM = SVC()
param_SVM = dict(reduce_dim__n_components=[2,3,4], clf__kernel=['linear', 'rbf', 'sigmoid'], clf__C=[1,10,100,1000,10000])

# Auto param selection.
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler   

def param_selection(clf, param_grid, X, Y):
    estimators = [('scaler', MinMaxScaler()), ('reduce_dim', PCA()), ('clf', clf)]
    model = Pipeline(estimators)
    
    selection = GridSearchCV(model, param_grid=param_grid, scoring='recall', cv=5)
    selection.fit(X, Y)
    print "Best params:"
    print selection.best_params_
    print
    print "Best estimator steps:"
    print selection.best_estimator_.named_steps

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!
features_train = []
features_test  = []
labels_train   = []
labels_test    = []

from sklearn.cross_validation import KFold
kf = KFold(len(labels), 10, shuffle=True, random_state=42)
for train_indices,  test_indices in kf:
    features_train = [features[ii] for ii in train_indices]
    features_test = [features[ii] for ii in test_indices]
    labels_train = [labels[ii] for ii in train_indices]
    labels_test = [labels[ii] for ii in test_indices]

##################################
# Feature selection
##################################
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif, chi2
feature_selection = SelectKBest(f_classif, k=13)
features_train_new = MinMaxScaler().fit_transform(features_train)
feature_selection.fit(features_train, labels_train)


selection_result = zip(feature_selection.scores_, features_list[1:])
selection_result.sort(key=lambda x:x[0], reverse=True) 

for s in selection_result:
    print s

print
print feature_selection.get_params()

# New features.
features_train_new = feature_selection.transform(features_train)
features_test_new = feature_selection.transform(features_test)

from time import time
t0 = time()
param_selection(clf_NB, param_NB, features_train, labels_train)
print 'NB param selection time:', round(time()-t0, 3), "s"

t0 = time()
param_selection(clf_DT, param_DT, features_train, labels_train)
print 'DT param selection time:', round(time()-t0, 3), "s"

t0 = time()
param_selection(clf_SVM, param_SVM, features_train, labels_train)
print 'SVM param selection time:', round(time()-t0, 3), "s"

############################
# Build models
############################
# Build model
### Use Scaler(), PCA(), GridSerchCV() to make model.
def NB_model():
    estimators = [('scaler', MinMaxScaler()), ('reduce_dim', PCA(n_components=4)),
                  ('clf', GaussianNB())]
    model = Pipeline(estimators)
    return model

def DT_model():
    estimators = [('scaler', MinMaxScaler()), ('reduce_dim', PCA(n_components=2)), 
                  ('clf', DecisionTreeClassifier(min_samples_split=20))]
    model = Pipeline(estimators)
    return model

def SVM_model():
    estimators = [('scaler', MinMaxScaler()), ('reduce_dim', PCA(n_components=2)), 
                  ('clf', SVC(C=10000, kernel='sigmoid'))]
    model = Pipeline(estimators)
    return model

# Train Fuction. 
def train_model(model):
    model.fit(features_train, labels_train)

    pred = model.predict(features_test)

    from sklearn.metrics import accuracy_score
    acc = accuracy_score(pred, labels_test)
    print "ACC:{0}".format(acc)

######################
# Training...
######################
nb_model = NB_model()
dt_model = DT_model()
svm_model = SVM_model()

print 'nb model training...'
train_model(nb_model)
print 

print 'dt model training...'
train_model(dt_model)
print 

print 'svm model training...'
train_model(svm_model)
print
### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

# Choose model.
clf = nb_model

dump_classifier_and_data(clf, my_dataset, features_list)