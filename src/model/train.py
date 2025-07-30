# Import libraries

import argparse
import glob
import os

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import mlflow
import mlflow.sklearn

# define functions
def main(args):
    # TO DO: enable autologging
    
    # Enable autologging
    mlflow.sklearn.autolog()

    with mlflow.start_run():
        #log parameters
        mlflow.log_param("training_data_path", args.training_data)
        mlflow.log_param("reg_rate", args.reg_rate)
        mlflow.log_param("regularization_C", 1/args.reg_rate)

        # read data
        print(f"Training data path: {args.training_data}")
        df = get_csvs_df(args.training_data)

        # Log dataset info
        mlflow.log_param("total_samples", len(df))
        mlflow.log_param("total_features", len(df.columns))
        
        # Check class distribution
        class_counts = df['Diabetic'].value_counts().sort_index()
        mlflow.log_param("class_0_count", class_counts[0])
        mlflow.log_param("class_1_count", class_counts[1])
        mlflow.log_param("class_balance_ratio", class_counts[1]/class_counts[0])
        
        # split data
        X_train, X_test, y_train, y_test = split_data(df)

        # Log split info
        mlflow.log_param("train_samples", len(X_train))
        mlflow.log_param("test_samples", len(X_test))
        mlflow.log_param("test_size_ratio", 0.30)

        # train model
        model = train_model(args.reg_rate, X_train, X_test, y_train, y_test)

        # Make predictions and log additional metrics
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Calculate and log custom metrics
        test_accuracy = accuracy_score(y_test, y_pred)
        test_auc = roc_auc_score(y_test, y_pred_proba)
        
        mlflow.log_metric("test_accuracy", test_accuracy)
        mlflow.log_metric("test_auc", test_auc)
        
        print(f"Model trained successfully!")
        print(f"Test Accuracy: {test_accuracy:.4f}")
        print(f"Test AUC: {test_auc:.4f}")
        print(f"MLflow Run ID: {mlflow.active_run().info.run_id}")

def get_csvs_df(path):
    if not os.path.exists(path):
        raise RuntimeError(f"Cannot use non-existent path provided: {path}")
    csv_files = glob.glob(f"{path}/*.csv")
    if not csv_files:
        raise RuntimeError(f"No CSV files found in provided data path: {path}")
    
    # Log number of CSV files found
    mlflow.log_param("csv_files_count", len(csv_files))
    mlflow.log_param("csv_files", [os.path.basename(f) for f in csv_files])

    return pd.concat((pd.read_csv(f) for f in csv_files), sort=False)

def split_data(df):
    feature_columns = ['Pregnancies','PlasmaGlucose','DiastolicBloodPressure',
                      'TricepsThickness','SerumInsulin','BMI','DiabetesPedigree','Age']
    
    # Log feature columns
    mlflow.log_param("feature_columns", feature_columns)
    mlflow.log_param("target_column", "Diabetic")
    
    # split data
    X, y = df[feature_columns].values, df['Diabetic'].values

    # split data in 70% for training and 30% for testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=0)
    return X_train, X_test, y_train, y_test

def train_model(reg_rate, X_train, X_test, y_train, y_test):
    # create model you want to use in this case LogisticRegression
    model =LogisticRegression(C=1/reg_rate, solver="liblinear").fit(X_train, y_train)
    
    # train model
    model.fit(X_train, y_train)

    # Return the model so we can use it for predictions
    return model

def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--training_data", dest='training_data',
                        type=str, required=True,
                        help="Path to directory containing CSV training data")
    parser.add_argument("--reg_rate", dest='reg_rate',
                        type=float, default=0.1,
                        help="Regularization rate (default: 0.1)")
    parser.add_argument("--experiment_name", dest='experiment_name',
                        type=str, default="diabetes_prediction",
                        help="MLflow experiment name (default: diabetes_prediction)")

    # parse args
    args = parser.parse_args()

    # return args
    return args

# run script
if __name__ == "__main__":
    # add space in logs
    print("\n\n")
    print("*" * 60)

    # parse args
    args = parse_args()
    
    # Set MLflow experiment
    mlflow.set_experiment(args.experiment_name)

    # run main function
    main(args)

    # add space in logs
    print("*" * 60)
    print("\n\n")
