# 🏠 Local MLflow Workflow

> **Alternative Option C**: Traditional local development with MLflow tracking

## 📖 Overview

This workflow allows you to train and track machine learning models entirely on your local machine using MLflow for experiment tracking. Perfect for rapid prototyping, debugging, and offline development.

## 🎯 When to Use This Workflow

- **Quick experimentation** without cloud dependencies
- **Debugging and development** with immediate feedback
- **Offline work** when cloud access is limited
- **Learning MLflow basics** before moving to cloud

## 🔧 Setup for Local Development

### 1. Environment Setup
```bash
# Navigate to project
cd experiment-mlops

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Local MLflow

⚠️ **IMPORTANT**: You need to modify `src/model/train.py` to enable local MLflow tracking.

Edit `src/model/train.py` with these changes:

#### **Enable Local Tracking URI (Line 16):**
```python
# UNCOMMENT this line for local MLflow
mlflow.set_tracking_uri("file:./mlruns")
```

#### **Add Manual Run Management (Lines 34-36):**
```python
def main(args):
    mlflow.sklearn.autolog()
    
    # FOR LOCAL: Manually manage MLflow runs
    with mlflow.start_run():
        run_training_workflow(args)
```

#### **Enable Experiment Setting (Lines 222-224):**
```python
# FOR LOCAL: Manually set experiment
try:
    mlflow.set_experiment(args.experiment_name)
    print(f"MLflow Experiment: {args.experiment_name}")
except Exception as e:
    print(f"Warning: Could not set experiment name, using default. Error: {e}")
```

### 3. Complete Local Configuration

Your modified `src/model/train.py` should look like this:

```python
# src/model/train.py - LOCAL CONFIGURATION

# Enable local tracking
mlflow.set_tracking_uri("file:./mlruns")

def main(args):
    mlflow.sklearn.autolog()
    
    # Manually manage runs for local development
    with mlflow.start_run():
        run_training_workflow(args)

# In main execution block:
if __name__ == "__main__":
    args = parse_args()
    
    # Set experiment manually for local
    mlflow.set_experiment(args.experiment_name)
    print(f"MLflow Experiment: {args.experiment_name}")
    
    main(args)
```

## 🏃‍♂️ Local Training Commands

### Basic Training
```bash
# Train with development data
python src/model/train.py --training_data ./experimentation/data

# Train with custom regularization
python src/model/train.py --training_data ./experimentation/data --reg_rate 0.05

# Train with production data
python src/model/train.py --training_data ./production/data --experiment_name production_model
```

### Command Line Arguments
| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--training_data` | ✅ | - | Path to directory containing CSV training data |
| `--reg_rate` | ❌ | 0.1 | Regularization rate (higher = more regularization) |
| `--experiment_name` | ❌ | diabetes_prediction | MLflow experiment name |

## 📊 Local MLflow UI

### Start MLflow UI
```bash
# Start MLflow dashboard
mlflow ui

# MLflow UI available at: http://127.0.0.1:5000
```

### View Experiments
1. Open http://127.0.0.1:5000
2. Browse experiments and runs
3. Compare model performance
4. Download model artifacts

## 🔄 Typical Development Workflow

### 1. Experiment Iteration
```bash
# Try different regularization values
python src/model/train.py --training_data ./experimentation/data --reg_rate 0.01
python src/model/train.py --training_data ./experimentation/data --reg_rate 0.1
python src/model/train.py --training_data ./experimentation/data --reg_rate 1.0

# Start MLflow UI to compare results
mlflow ui
```

### 2. Model Validation
```bash
# Train with production data after finding good parameters
python src/model/train.py --training_data ./production/data --reg_rate 0.01 --experiment_name production_validation
```

### 3. Results Analysis
- Open MLflow UI at http://127.0.0.1:5000
- Compare experiments side by side
- Download best performing models
- Export metrics for reporting

## 📈 What Gets Tracked Locally

### Automatic Tracking (via `mlflow.sklearn.autolog()`)
- ✅ **Model Parameters**: Algorithm settings, regularization
- ✅ **Training Metrics**: Loss curves, accuracy
- ✅ **Model Artifacts**: Trained model files
- ✅ **Dataset Information**: Data shape, features

### Custom Tracking (via manual logging)
- ✅ **Test Metrics**: `test_accuracy`, `test_auc`
- ✅ **Custom Parameters**: Data paths, experiment settings
- ✅ **Artifacts**: Plots, confusion matrices

## ⚠️ Important Warnings

### **This Configuration Breaks Azure ML**
If you make these local changes, you **CANNOT** submit jobs to Azure ML without reverting the changes first.

### **Mode Switching Required**
To switch between local and Azure ML modes, you need to:

#### **Local → Azure ML**
1. **Comment out tracking URI**:
   ```python
   # mlflow.set_tracking_uri("file:./mlruns")  # Only for local runs
   ```

2. **Remove manual run management**:
   ```python
   def main(args):
       mlflow.sklearn.autolog()
       # No with mlflow.start_run(): wrapper
       run_training_workflow(args)
   ```

3. **Disable experiment setting**:
   ```python
   print(f"Azure ML will use experiment from job-dev.yml: {args.experiment_name}")
   # No mlflow.set_experiment() call
   ```

## 🛠️ Troubleshooting

### MLflow UI Issues
```bash
# If MLflow UI won't start
mlflow ui --port 5001  # Try different port

# If experiments not showing
mlflow ui --backend-store-uri ./mlruns  # Specify explicit path
```

### Training Script Issues
```bash
# If import errors
pip install -r requirements.txt

# If MLflow tracking errors
# Ensure virtual environment is activated
# Check that mlflow.set_tracking_uri() is uncommented
```

### Data Loading Issues
- Ensure CSV files exist in specified data directory
- Check file permissions
- Verify data format matches expected structure

## 🎯 Best Practices for Local Development

### 1. Experiment Organization
```bash
# Use descriptive experiment names
python src/model/train.py --training_data ./experimentation/data --experiment_name "regularization_tuning"
python src/model/train.py --training_data ./experimentation/data --experiment_name "feature_engineering"
```

### 2. Parameter Exploration
```bash
# Systematic parameter exploration
for reg_rate in 0.01 0.1 1.0; do
    python src/model/train.py --training_data ./experimentation/data --reg_rate $reg_rate
done
```

### 3. Data Validation
```bash
# Always test with both datasets
python src/model/train.py --training_data ./experimentation/data  # Development
python src/model/train.py --training_data ./production/data       # Production
```

## 📊 Expected Results

From local training you should see:
- **Test Accuracy**: ~78-80%
- **Test AUC**: ~85-87%
- **Model Type**: Logistic Regression with L2 regularization
- **MLflow UI**: Experiments with detailed metrics and artifacts

## 🔗 Related Documentation

- **Main README.md**: GitHub Actions workflow (recommended)
- **README_AZURE_ML_DIRECT.md**: Direct Azure ML workflow
- **MLflow Documentation**: https://mlflow.org/docs/latest/

## 🎓 Learning Path

1. **Start Here**: Get comfortable with local MLflow tracking
2. **Next**: Try [README_AZURE_ML_DIRECT.md](README_AZURE_ML_DIRECT.md) for cloud training
3. **Advanced**: Use [main README.md](README.md) for full CI/CD pipeline

---

**💡 Tip**: Use this workflow for rapid prototyping, then move to cloud workflows for production MLOps!
