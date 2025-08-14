# Diabetes Prediction MLOps Project

This project demonstrates MLOps practices for training and tracking machine learning models using Azure Machine Learning, Python, scikit-learn, and MLflow. It supports both **Azure ML Cloud** and **Local MLflow** workflows.

## 🏗️ Project Structure

```
experiment-mlops/
├── src/
│   ├── model/
│   │   └── train.py          # Main training script with MLflow tracking
│   └── job.yml              # Azure ML job configuration
├── experimentation/
│   └── data/                # Development dataset (diabetes-dev.csv)
├── production/
│   └── data/                # Production dataset (diabetes-prod.csv)
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
├── mlruns/                 # Local MLflow tracking directory
└── README.md               # This file
```

## 🚀 Quick Start Options

### Option A: Azure Machine Learning (Cloud)
### Option B: Local MLflow (Traditional)

---

# 🌩️ Azure Machine Learning Workflow

## Prerequisites

1. **Azure ML Workspace** - Create via Azure Portal
2. **Azure CLI** - 64-bit version with ML extension
3. **Compute Instance** - For running training jobs

## 🔧 Setup Azure CLI

### 1. Install Azure CLI (64-bit)
```powershell
# Uninstall old version first
winget uninstall Microsoft.AzureCLI

# Install latest 64-bit version
winget install Microsoft.AzureCLI

# Verify installation
az --version
# Should show: Python (Windows) 3.x.x [MSC v.xxxx 64 bit (AMD64)]
```

### 2. Install ML Extension
```powershell
# Install Azure ML extension
az extension add -n ml

# Verify ML extension
az extension list | findstr ml
```

### 3. Authenticate
```powershell
# Login to Azure
az login --scope https://management.azure.com/.default

# Verify authentication
az account show
```

## 📊 Data Asset Registration

### Register Development Dataset
```powershell
az ml data create \
  --name diabetes-dev-folder \
  --path ./experimentation/data \
  --type uri_folder \
  --workspace-name <your-workspace-name> \
  --resource-group <your-resource-group>
```

### Register Production Dataset
```powershell
az ml data create \
  --name diabetes-prod-folder \
  --path ./production/data \
  --type uri_folder \
  --workspace-name <your-workspace-name> \
  --resource-group <your-resource-group>
```

### Verify Data Assets
```powershell
az ml data list \
  --workspace-name <your-workspace-name> \
  --resource-group <your-resource-group>
```

## 💻 Compute Instance Creation

### Via Azure ML Studio
1. Navigate to **Azure ML Studio** → **Compute** → **Compute Instances**
2. Click **+ New**
3. Choose VM size:
   - **Standard_DS3_v2** (Recommended for learning)
   - 4 cores, 14GB RAM, good for small datasets
4. Name: `diabetes-compute-instance`
5. Click **Create**

### Via Azure CLI
```powershell
az ml compute create \
  --name diabetes-compute-instance \
  --type ComputeInstance \
  --size Standard_DS3_v2 \
  --workspace-name <your-workspace-name> \
  --resource-group <your-resource-group>
```

## ⚙️ Job Configuration

### Edit `src/job.yml`
```yaml
$schema: https://azuremlschemas.azureedge.net/latest/commandJob.schema.json
code: ./model
command: python train.py --training_data ${{inputs.training_data}} --reg_rate ${{inputs.reg_rate}}
inputs:
  training_data:
    type: uri_folder
    path: azureml:diabetes-dev-folder@latest  # Use your data asset
  reg_rate: 0.01
environment: azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu@latest
compute: azureml:diabetes-compute-instance    # Use your compute instance name
experiment_name: diabetes-prediction
description: Train a diabetes prediction model using logistic regression with MLflow tracking
```

## 🏃‍♂️ Submit Training Job

### Basic Job Submission
```powershell
az ml job create \
  --file src/job.yml \
  --resource-group <your-resource-group> \
  --workspace-name <your-workspace-name>
```

### Monitor Job
The command returns a Studio URL to monitor your job:
```
https://ml.azure.com/runs/<job-name>?wsid=/subscriptions/.../workspaces/<workspace>
```

### Check Job Status
```powershell
az ml job show \
  --name <job-name> \
  --workspace-name <your-workspace-name> \
  --resource-group <your-resource-group>
```

## 📈 Azure ML MLflow Integration

### How It Works
- **Automatic Integration**: Azure ML automatically configures MLflow
- **Managed Runs**: Azure ML creates and manages MLflow runs
- **No Manual Setup**: Don't call `mlflow.start_run()` or set tracking URI
- **Built-in UI**: View metrics in Azure ML Studio

### What Gets Tracked
- ✅ **Model Parameters**: Automatically via `mlflow.sklearn.autolog()`
- ✅ **Training Metrics**: Loss, accuracy from sklearn
- ✅ **Custom Metrics**: `test_accuracy`, `test_auc` via `mlflow.log_metric()`
- ✅ **Model Artifacts**: Trained model saved automatically
- ✅ **Code Snapshots**: Training script and environment

### View Results
1. **Azure ML Studio**: Navigate to your job → **Metrics** tab
2. **MLflow UI**: Use the tracking endpoint provided in job output
3. **Experiments**: View all runs under the experiment name

## 🔄 Re-running Jobs

### Re-run Same Configuration
```powershell
# Creates a new job with same settings
az ml job create \
  --file src/job.yml \
  --resource-group <your-resource-group> \
  --workspace-name <your-workspace-name>
```

### Re-run with Different Parameters
```yaml
# Edit src/job.yml to change:
inputs:
  reg_rate: 0.05  # Different regularization
  # Or change data asset to production data
  training_data:
    path: azureml:diabetes-prod-folder@latest
```

### Clone from Azure ML Studio
1. Go to **Jobs** → Select completed job
2. Click **Clone** → Modify parameters
3. Click **Submit**

---

# 🏠 Local MLflow Workflow (Alternative)

## 🔧 Setup for Local Development

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure Local MLflow
Edit `src/model/train.py` to enable local MLflow:

```python
# Uncomment for local MLflow tracking
mlflow.set_tracking_uri("file:./mlruns")

# Use manual run management for local
def main(args):
    mlflow.sklearn.autolog()
    
    # For local development, manually manage runs
    with mlflow.start_run():
        run_training_workflow(args)
```

## 🏃‍♂️ Local Training Commands

### Basic Training
```powershell
# Train with development data
python .\src\model\train.py --training_data .\experimentation\data

# Train with custom regularization
python .\src\model\train.py --training_data .\experimentation\data --reg_rate 0.05

# Train with production data
python .\src\model\train.py --training_data .\production\data --experiment_name production_model
```

### Command Line Arguments
| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--training_data` | ✅ | - | Path to directory containing CSV training data |
| `--reg_rate` | ❌ | 0.1 | Regularization rate (higher = more regularization) |
| `--experiment_name` | ❌ | diabetes_prediction | MLflow experiment name |

## 📊 Local MLflow UI

### Start MLflow UI
```powershell
# Start MLflow dashboard
mlflow ui

# MLflow UI available at: http://127.0.0.1:5000
```

### View Experiments
1. Open http://127.0.0.1:5000
2. Browse experiments and runs
3. Compare model performance
4. Download model artifacts

---

# 🔀 Switching Between Azure ML and Local MLflow

## Azure ML → Local MLflow

### 1. Modify `train.py`
```python
# Uncomment this line for local development
mlflow.set_tracking_uri("file:./mlruns")

# Change main function to use manual run management
def main(args):
    mlflow.sklearn.autolog()
    
    # For local: manually start runs
    with mlflow.start_run():
        run_training_workflow(args)
```

### 2. Run Locally
```powershell
python .\src\model\train.py --training_data .\experimentation\data
```

## Local MLflow → Azure ML

### 1. Revert `train.py`
```python
# Comment out for Azure ML
# mlflow.set_tracking_uri("file:./mlruns")

# Let Azure ML manage runs automatically
def main(args):
    mlflow.sklearn.autolog()
    
    # For Azure ML: no manual run management
    run_training_workflow(args)
```

### 2. Submit to Azure ML
```powershell
az ml job create \
  --file src/job.yml \
  --resource-group <your-resource-group> \
  --workspace-name <your-workspace-name>
```

---

# 📊 Model Performance & Results

## Expected Results
From the diabetes prediction model:
- **Test Accuracy**: ~78-80%
- **Test AUC**: ~85-87%
- **Model Type**: Logistic Regression with L2 regularization

## Dataset Information
**Features** (8 input variables):
- `Pregnancies`: Number of pregnancies
- `PlasmaGlucose`: Glucose concentration 
- `DiastolicBloodPressure`: Blood pressure (mm Hg)
- `TricepsThickness`: Skin fold thickness (mm)
- `SerumInsulin`: Insulin level (mu U/ml)
- `BMI`: Body mass index
- `DiabetesPedigree`: Diabetes pedigree function
- `Age`: Age (years)

**Target**: `Diabetic` (0 = No diabetes, 1 = Has diabetes)

## Model Configuration
- **Algorithm**: Logistic Regression
- **Solver**: liblinear (good for small datasets)
- **Regularization**: L2 (Ridge) with configurable strength
- **Train/Test Split**: 70/30 with fixed random state

---

# 🛠️ Troubleshooting

## Azure CLI Issues

### 32-bit vs 64-bit CLI
```powershell
# Check if you have 64-bit CLI
az --version
# Should show: Python (Windows) 3.x.x [MSC v.xxxx 64 bit (AMD64)]

# If shows 32-bit, reinstall:
winget uninstall Microsoft.AzureCLI
winget install Microsoft.AzureCLI
```

### Missing Dependencies
```powershell
# Install missing Python packages
pip install rpds-py pywin32

# Run pywin32 post-install (if needed)
python Scripts/pywin32_postinstall.py -install
```

### Authentication Expired
```powershell
# Re-authenticate
az login --scope https://management.azure.com/.default
```

## Job Submission Issues

### Missing Arguments Error
```powershell
# Always include resource group and workspace
az ml job create \
  --file src/job.yml \
  --resource-group <your-resource-group> \
  --workspace-name <your-workspace-name>
```

### Compute Instance Not Found
Update `src/job.yml`:
```yaml
compute: azureml:<your-actual-compute-instance-name>
```

### Data Asset Not Found
```powershell
# Verify data asset exists
az ml data list \
  --workspace-name <your-workspace-name> \
  --resource-group <your-resource-group>
```

## MLflow Issues

### No Metrics in Azure ML Studio
This can happen when:
- MLflow logging fails silently
- Autolog doesn't capture custom metrics
- Run management conflicts

**Solution**: Check job logs in Azure ML Studio → **Outputs + logs** tab

### Local MLflow UI Shows Wrong Experiments
```powershell
# Use correct tracking directory
mlflow ui                                    # Current runs (./mlruns)
mlflow ui --backend-store-uri ./src/model/mlruns  # Legacy runs
```

## Training Script Issues

### Import Errors
```powershell
# Install dependencies
pip install -r requirements.txt

# Verify Python environment
python --version  # Should be 3.8+
```

### Data Loading Errors
- Ensure CSV files exist in data directory
- Check file permissions
- Verify data format (headers, column names)

---

# 🧪 Testing

## Run Unit Tests
```powershell
pytest tests/
```

## Test Training Script
```powershell
# Test with small dataset
python .\src\model\train.py --training_data .\tests\datasets
```

---

# 📚 Additional Resources

## Azure ML Documentation
- [Azure ML CLI v2](https://docs.microsoft.com/en-us/azure/machine-learning/reference-azure-machine-learning-cli)
- [Azure ML Jobs](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-train-model)
- [Azure ML Data Assets](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-create-data-assets)

## MLflow Documentation  
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow with Azure ML](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-mlflow)
- [MLflow Autologging](https://mlflow.org/docs/latest/tracking.html#automatic-logging)

## Commands Reference

### Azure ML Commands
```powershell
# List workspaces
az ml workspace list

# List data assets
az ml data list -w <workspace> -g <resource-group>

# List compute instances  
az ml compute list -w <workspace> -g <resource-group>

# List jobs
az ml job list -w <workspace> -g <resource-group>

# Show specific job
az ml job show -n <job-name> -w <workspace> -g <resource-group>

# Cancel running job
az ml job cancel -n <job-name> -w <workspace> -g <resource-group>
```

### Local Development
```powershell
# Train model locally
python .\src\model\train.py --training_data .\experimentation\data

# Start MLflow UI
mlflow ui

# Run tests
pytest tests/

# Install dependencies
pip install -r requirements.txt
```

---

# 🎯 Success Criteria

You have successfully completed this MLOps workflow when you can:

1. ✅ **Register data assets** in Azure ML
2. ✅ **Submit training jobs** via Azure CLI
3. ✅ **Monitor job execution** in Azure ML Studio
4. ✅ **View training metrics** and results
5. ✅ **Switch between Azure ML and local MLflow** workflows
6. ✅ **Re-run experiments** with different parameters

**Congratulations!** You've implemented a complete MLOps pipeline with Azure Machine Learning! 🚀

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

This project is for educational purposes demonstrating MLOps practices with Azure Machine Learning.