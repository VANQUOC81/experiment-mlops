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

# In Azure ML, MLflow tracking is automatically configured
# Comment out the local tracking URI to use Azure ML's managed MLflow
# mlflow.set_tracking_uri("file:./mlruns")  # Only for local runs

# define functions


def main(args):
    """
    Main training function that:
    1. Enables MLflow autologging for sklearn models
    2. Starts an MLflow run to track the experiment
    3. Logs parameters, metrics, and model artifacts
    4. Trains a logistic regression model for diabetes prediction

    Args:
        args: Parsed command line arguments containing training_data path and reg_rate
    """

    # Enable MLflow autologging - automatically logs model parameters,
    # metrics, and artifacts
    mlflow.sklearn.autolog()

    # Azure ML automatically manages MLflow runs, so we don't need to start one manually
    # Just run the training workflow directly
    run_training_workflow(args)


def run_training_workflow(args):
    """
    Execute the training workflow with MLflow logging.
    This function contains the actual training logic that 
    was previously in the mlflow.start_run() context.
    """
    # Log custom parameters for this training run
    mlflow.log_param("training_data_path", args.training_data)
    mlflow.log_param("reg_rate", args.reg_rate)
    mlflow.log_param("regularization_C", 1 / args.reg_rate)

    # Load and prepare data
    print(f"Training data path: {args.training_data}")
    df = get_csvs_df(args.training_data)

    # Log dataset information for tracking
    mlflow.log_param("total_samples", len(df))
    mlflow.log_param("total_features", len(df.columns))

    # Analyze and log class distribution (important for imbalanced datasets)
    class_counts = df['Diabetic'].value_counts().sort_index()
    mlflow.log_param("class_0_count", class_counts[0])
    mlflow.log_param("class_1_count", class_counts[1])
    mlflow.log_param("class_balance_ratio", class_counts[1] / class_counts[0])

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = split_data(df)

    # Log data split information
    mlflow.log_param("train_samples", len(X_train))
    mlflow.log_param("test_samples", len(X_test))
    mlflow.log_param("test_size_ratio", 0.30)

    # Train the logistic regression model
    model = train_model(args.reg_rate, X_train, X_test, y_train, y_test)

    # Make predictions on test set for evaluation
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[
        :, 1]  # Get probabilities for positive class

    # Calculate and log additional custom metrics beyond what autolog captures
    test_accuracy = accuracy_score(y_test, y_pred)
    test_auc = roc_auc_score(y_test, y_pred_proba)

    mlflow.log_metric("test_accuracy", test_accuracy)
    mlflow.log_metric("test_auc", test_auc)

    # Print results summary
    print(f"Model trained successfully!")
    print(f"Test Accuracy: {test_accuracy:.4f}")
    print(f"Test AUC: {test_auc:.4f}")

    # Print MLflow run ID if available
    active_run = mlflow.active_run()
    if active_run:
        print(f"MLflow Run ID: {active_run.info.run_id}")
    else:
        print("MLflow run information not available")
    print(f"View results: Azure ML Studio")


def get_csvs_df(path):
    """
    Load all CSV files from the specified directory and combine them into a single DataFrame.

    Args:
        path (str): Directory path containing CSV files

    Returns:
        pd.DataFrame: Combined DataFrame from all CSV files

    Raises:
        RuntimeError: If path doesn't exist or no CSV files found
    """
    if not os.path.exists(path):
        raise RuntimeError(f"Cannot use non-existent path provided: {path}")
    csv_files = glob.glob(f"{path}/*.csv")
    if not csv_files:
        raise RuntimeError(f"No CSV files found in provided data path: {path}")

    # Log file information for tracking data sources
    mlflow.log_param("csv_files_count", len(csv_files))
    mlflow.log_param("csv_files", [os.path.basename(f) for f in csv_files])

    return pd.concat((pd.read_csv(f) for f in csv_files), sort=False)


def split_data(df):
    """
    Split the diabetes dataset into features and target, then into train/test sets.

    Args:
        df (pd.DataFrame): Input DataFrame containing diabetes data

    Returns:
        tuple: X_train, X_test, y_train, y_test arrays
    """
    # Define feature columns used for prediction
    feature_columns = [
        'Pregnancies',
        'PlasmaGlucose',
        'DiastolicBloodPressure',
        'TricepsThickness',
        'SerumInsulin',
        'BMI',
        'DiabetesPedigree',
        'Age']

    # Log feature information for reproducibility
    mlflow.log_param("feature_columns", feature_columns)
    mlflow.log_param("target_column", "Diabetic")

    # Extract features (X) and target (y) from DataFrame
    X, y = df[feature_columns].values, df['Diabetic'].values

    # Split data: 70% training, 30% testing (fixed random_state for
    # reproducibility)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=0)
    return X_train, X_test, y_train, y_test


def train_model(reg_rate, X_train, X_test, y_train, y_test):
    """
    Train a Logistic Regression model for diabetes prediction.

    Args:
        reg_rate (float): Regularization rate (higher = more regularization)
        X_train, X_test: Training and test feature arrays
        y_train, y_test: Training and test target arrays

    Returns:
        sklearn.linear_model.LogisticRegression: Trained model
    """
    # Create and train Logistic Regression model
    # C = 1/reg_rate (lower C = more regularization)
    # liblinear solver works well for small datasets
    model = LogisticRegression(C=1 / reg_rate, solver="liblinear")
    model.fit(X_train, y_train)

    return model


def parse_args():
    """
    Parse command line arguments for the training script.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Train a diabetes prediction model with MLflow tracking",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Required arguments
    parser.add_argument("--training_data", dest='training_data',
                        type=str, required=True,
                        help="Path to directory containing CSV training data")

    # Optional arguments
    parser.add_argument(
        "--reg_rate",
        dest='reg_rate',
        type=float,
        default=0.05,
        help="Regularization rate (higher = more regularization)")
    parser.add_argument("--experiment_name", dest='experiment_name',
                        type=str, default="diabetes_prediction",
                        help="MLflow experiment name")

    return parser.parse_args()


# Main execution
if __name__ == "__main__":
    """
    Main script execution:
    1. Parse command line arguments
    2. Set MLflow experiment 
    3. Run training with MLflow tracking
    """
    print("\n" + "=" * 60)
    print("DIABETES PREDICTION MODEL TRAINING")
    print("=" * 60)

    # Parse command line arguments
    args = parse_args()

    # In Azure ML, experiment is automatically set via job.yml
    # Don't manually set experiment - let Azure ML manage it
    print(f"Azure ML will use experiment from job.yml: {args.experiment_name}")

    # Run main training function
    main(args)

    print("=" * 60)
    print("TRAINING COMPLETED")
    print("=" * 60 + "\n")
