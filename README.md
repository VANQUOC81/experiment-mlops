# Diabetes Prediction MLOps Project

This project demonstrates MLOps practices for training and tracking machine learning models using Python, scikit-learn, and MLflow.

## Project Structure

```
experiment-mlops/
├── src/model/
│   ├── train.py          # Main training script with MLflow tracking
│   └── mlruns/          # MLflow experiments (legacy location)
├── experimentation/
│   └── data/            # Development dataset
├── production/
│   └── data/            # Production dataset  
├── tests/               # Unit tests
├── requirements.txt     # Python dependencies
├── mlruns/             # MLflow tracking directory (current)
└── README.md           # This file
```

## Quick Start

### 1. Install Dependencies

```powershell
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Train a Model

From the project root directory:

```powershell
# Basic training with development data
python .\src\model\train.py --training_data .\experimentation\data

# Training with custom parameters
python .\src\model\train.py --training_data .\experimentation\data --reg_rate 0.05 --experiment_name my_experiment

# Training with production data
python .\src\model\train.py --training_data .\production\data --experiment_name production_model
```

### 3. View Results in MLflow

```powershell
# Start MLflow UI
mlflow ui

# MLflow UI will be available at: http://127.0.0.1:5000
```

## Command Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--training_data` | ✅ | - | Path to directory containing CSV training data |
| `--reg_rate` | ❌ | 0.1 | Regularization rate (higher = more regularization) |
| `--experiment_name` | ❌ | diabetes_prediction | MLflow experiment name |

## Example Commands

```powershell
# Help information
python .\src\model\train.py --help

# Quick training with defaults
python .\src\model\train.py --training_data .\experimentation\data

# Training with lower regularization
python .\src\model\train.py --training_data .\experimentation\data --reg_rate 0.01

# Training with custom experiment name
python .\src\model\train.py --training_data .\experimentation\data --experiment_name diabetes_model_v3
```

## MLflow Tracking

This project automatically tracks:

### Parameters
- Training data path and file information
- Model hyperparameters (regularization rate, solver, etc.)
- Dataset statistics (total samples, features, class distribution)
- Data split information (train/test ratios)

### Metrics
- Test accuracy
- Test AUC (Area Under Curve)
- Training metrics (automatically logged by MLflow autolog)

### Artifacts
- Trained model (pickle format)
- Model performance plots (confusion matrix, ROC curve, etc.)
- Model metadata and signature

## MLflow UI Guide

### Accessing the Dashboard
1. Run `mlflow ui` from the project root
2. Open http://127.0.0.1:5000 in your browser
3. Browse experiments and runs

### Understanding the Interface
- **Experiments**: Groups of related model runs
- **Runs**: Individual training sessions with tracked parameters/metrics
- **Models**: Registered models for deployment
- **Compare**: Side-by-side comparison of multiple runs

### Experiment Locations
- **Current runs**: Saved to `./mlruns` (use `mlflow ui`)
- **Legacy runs**: Saved to `./src/model/mlruns` (use `mlflow ui --backend-store-uri .\src\model\mlruns`)

## Dataset Information

The project works with diabetes prediction datasets containing these features:
- `Pregnancies`: Number of pregnancies
- `PlasmaGlucose`: Glucose concentration 
- `DiastolicBloodPressure`: Blood pressure (mm Hg)
- `TricepsThickness`: Skin fold thickness (mm)
- `SerumInsulin`: Insulin level (mu U/ml)
- `BMI`: Body mass index
- `DiabetesPedigree`: Diabetes pedigree function
- `Age`: Age (years)

Target variable: `Diabetic` (0 = No, 1 = Yes)

## Model Details

- **Algorithm**: Logistic Regression
- **Solver**: liblinear (good for small datasets)
- **Regularization**: L2 (Ridge) with configurable strength
- **Train/Test Split**: 70/30 with fixed random state for reproducibility

## Troubleshooting

### MLflow UI shows wrong experiments
- Check which tracking directory you're pointing to:
  - Current: `mlflow ui` (uses `./mlruns`)
  - Legacy: `mlflow ui --backend-store-uri .\src\model\mlruns`

### Dependencies installation fails
- Use pre-built wheels: `pip install --only-binary=all -r requirements.txt`
- Update pip first: `python -m pip install --upgrade pip`

### Training script errors
- Ensure you're running from the project root directory
- Check that the data directory contains CSV files
- Verify Python version compatibility (3.8+)

## Testing

Run unit tests:
```powershell
pytest tests/
```

## Dependencies

- `pytest>=7.1.2`: Testing framework
- `mlflow>=2.14.1`: Experiment tracking and model management
- `pandas>=2.1.0`: Data manipulation
- `scikit-learn==1.7.0`: Machine learning library

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run existing tests to ensure compatibility
5. Submit a pull request

## License

This project is for educational purposes demonstrating MLOps practices.
