import pandas as pd
import pickle
from sklearn.model_selection import train_test_split, RandomizedSearchCV, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve
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
                    "recall": round (precision, 2),
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

loaded_pickle_model = pickle.load(open("heart_failure.pkl", "rb"))
pickle_y_preds = loaded_pickle_model.predict(X_test)
evaluate_preds(y_test, pickle_y_preds)