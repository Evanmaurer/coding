import pandas as pd
import pickle
from sklearn.model_selection import train_test_split, RandomizedSearchCV, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import numpy as np

def plot_roc_curve (fpr,tpr):
    """
    plots ROC curve give flase pos rate and true pos rate 
    """
    plt.plot(fpr, tpr, color = "orange", label = "ROC")
    plt.plot ([0,1],[0,1], color="darkblue", linestyle="--", label= "guessing")
    plt.xlabel("Falase positive rate (fpr)")
    plt.ylabel("True positive rate (tpr)")
    plt.title("ROC curve")
    plt.legend()
    plt.show()
def evaluate_preds(y_true, y_preds):
    accuracy = accuracy_score(y_true, y_preds)
    precision = precision_score(y_true, y_preds)
    recall = recall_score(y_true, y_preds)
    f1 = f1_score(y_true, y_preds)
    metric_disct = {"accuracy": round (accuracy, 2),
                    "precision": round(precision, 2),
                    "recall": round (recall, 2),
                    "f1":round(f1, 2)}
    print(f"Acc: {accuracy *100:.2f}%")
    print (f"Precision:{precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 score: {f1:.2f}")
    return metric_disct

df = pd.read_csv('heart_failure_clinical_records_dataset.csv', encoding = 'latin-1')
grid = {"n_estimators": [10, 100, 200, 500, 1000, 1200],
        "max_depth": [None, 5, 10, 20,30],
        "max_features": ["log2","sqrt"],
        "min_samples_split": [2,4,6],
        "min_samples_leaf":[1,2,4]}
grid_2 = {"n_estimators": [ 100, 200, 500, 1200],
        "max_depth": [None,20],
        "max_features": ["sqrt"],
        "min_samples_split": [2, 6],
        "min_samples_leaf":[1,2]}
X  = df.drop("DEATH_EVENT", axis=1)
y = df["DEATH_EVENT"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
clf = RandomForestClassifier(n_jobs=-1) # model choice 
clf.fit(X_train, y_train)
clf_cross_val_score = np.mean(cross_val_score(clf, X, y, cv=10))
y_probs = clf.predict_proba(X_test)
y_probs_positive = y_probs[:,1]
fpr, tpr, thresholds = roc_curve(y_test,y_probs_positive)
plot_roc_curve(fpr,tpr)
print(roc_auc_score(y_test,y_probs_positive))
rs_clf = RandomizedSearchCV(estimator=clf,
                            param_distributions=grid,
                            n_iter=30, #number of mobels to try 
                            cv=5,
                            verbose=2)
rs_clf.fit(X_train,y_train)
print(rs_clf.best_params_)
rs_y_preds = rs_clf.predict(X_test)
rs_metrics = evaluate_preds(y_test,rs_y_preds)
print (rs_metrics)
gs_clf = GridSearchCV(estimator=clf,
                            param_grid=grid_2,
                            cv=5,
                            verbose=2)
gs_clf.fit(X_train,y_train)
print(gs_clf.best_params_)
gs_y_preds = gs_clf.predict(X_test)
gs_metrics = evaluate_preds(y_test,gs_y_preds)
print(gs_metrics)
compare_metrics = pd.DataFrame({"random search": rs_metrics,
                               "grid search": gs_metrics})
print(compare_metrics.plot.bar(figsize=(10,8)))
pickle.dump(gs_clf, open("heart_failure.pkl", "wb"))
