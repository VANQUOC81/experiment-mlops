# Diabetes Prediction MLOps Project

This project demonstrates MLOps practices for training and tracking machine learning models using Azure Machine Learning, Python, scikit-learn, and MLflow. It supports three workflows:
- **GitHub Actions with Azure ML**: Automated cloud training via GitHub
- **Azure ML Direct**: Manual cloud training via Azure CLI
- **Local MLflow**: Traditional local development

## 🏗️ Project Structure

```
experiment-mlops/
├── .github/
│   └── workflows/
│       └── 02-manual-trigger-job.yml  # GitHub Actions workflow
├── src/
│   ├── model/
│   │   └── train.py                   # Main training script with MLflow tracking
│   └── job.yml                       # Azure ML job configuration
├── experimentation/
│   └── data/                         # Development dataset (diabetes-dev.csv)
├── production/
│   └── data/                         # Production dataset (diabetes-prod.csv)
├── tests/                            # Unit tests
├── requirements.txt                  # Python dependencies
├── mlruns/                          # Local MLflow tracking directory
└── README.md                        # This file
```

# ALWAYS WORK FROM PYTHON VIRTUAL ENVIRONMENT AND DEACTIVATE ONCE DONE!!! 

## 📋 Daily Development Workflow

### 🚀 Starting Development (First Time Setup)
```bash
# 1. Clone repository and navigate to project
git clone <repository-url>
cd experiment-mlops

# 2. Create feature branch (no virtual environment needed)
git checkout -b feature/your-feature-name

# 3. Create virtual environment
python -m venv venv

# 4. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 5. Install dependencies (needs virtual environment)
pip install -r requirements.txt

# 6. Verify setup (needs virtual environment)
python -m pytest -v
```

### 🌅 Daily Start (Continuing Development)
```bash
# 1. Navigate to project
cd D:\Projects\Github\experiment-mlops

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Verify environment (optional)
python -m pytest -v

# 4. Start developing!
```

#### 🖥️ **Cursor IDE Users** (VS Code Compatible):
- **Open Project**: `File > Open Folder` → Select `experiment-mlops`
- **Check Status Bar**: Should show `(venv)` and correct Python interpreter
- **Select Interpreter**: `Ctrl+Shift+P` → "Python: Select Interpreter" → Choose venv path
- **Integrated Terminal**: `Ctrl+`` ` (automatically activates virtual environment)

### 🌙 End of Day
```bash
# 1. Commit your work
git add .
git commit -m "Your commit message"
git push origin feature/your-feature-name

# 2. Deactivate virtual environment
deactivate

# 3. Close terminal/IDE
```

### 🔄 Next Day Continuation
```bash
# 1. Navigate to project
cd D:\Projects\Github\experiment-mlops

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Continue development
```

### ✅ Key Commands Reference
- **Activate**: `.\venv\Scripts\Activate.ps1`
- **Deactivate**: `deactivate`
- **Run tests**: `python -m pytest -v`
- **Check packages**: `pip list`
- **Install new package**: `pip install package-name`

---

## 🚀 Quick Start Options

### Option A: GitHub Actions with Azure ML (Recommended)
### Option B: Azure ML Direct (Alternative Cloud)
### Option C: Local MLflow (Traditional)

---

# 🤖 GitHub Actions with Azure ML (Recommended)

## Prerequisites

1. **Azure Resources**:
   - Azure ML workspace
   - Azure service principal with contributor access
   - Compute cluster (for automated training)
   - Registered data assets

2. **GitHub Setup**:
   - Fork/clone this repository
   - Create `AZURE_CREDENTIALS` secret

## 🔑 Service Principal Setup

### 1. Create Service Principal
```powershell
# Create service principal with contributor access
az ad sp create-for-rbac --name "mlops-github-sp" --role contributor \
    --scopes /subscriptions/<subscription-id>/resourceGroups/<resource-group> \
    --sdk-auth
```

### 2. Create GitHub Secret
1. Go to repository → **Settings** → **Secrets and variables** → **Actions**
2. Create new secret named `AZURE_CREDENTIALS`
3. Paste the entire JSON output from service principal creation

## ⚙️ Compute Cluster Setup

1. **Azure ML Studio**: Navigate to **Compute** → **Compute clusters**
2. Click **New**
3. Configure:
   - Name: `my-compute-cluster`
   - VM Size: `Standdjust based on needs)
4. Enable **Idle seconds befoard_DS3_v2` (recommended)
   - Min nodes: `0` (scales to zero when idle)
   - Max nodes: `1` (are scale down**

## 📊 Data Asset Registration
Same as Azure ML Direct workflow below.

## 🚀 Trigger Training

### Manual Trigger
1. Go to **Actions** → **Manually trigger an Azure Machine Learning job**
2. Click **Run workflow**
3. Monitor progress in GitHub Actions and Azure ML Studio

### View Results
- GitHub Actions: See workflow run logs
- Azure ML Studio: View detailed metrics and artifacts

# 🌩️ Azure ML Direct Workflow (Alternative)

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

## ⚠️ **Critical Understanding: Two Incompatible Modes**

Your `train.py` script can operate in **two mutually exclusive modes**:

1. **🌩️ Azure ML Mode**: Designed for Azure ML jobs (current configuration)
2. **🏠 Local MLflow Mode**: Designed for local development with manual MLflow

**You CANNOT mix these modes** - each requires specific configuration changes.

---

## 🌩️ **Current Configuration: Azure ML Mode**

### **How It Works:**
- ✅ **No tracking URI**: Azure ML automatically configures MLflow
- ✅ **No manual runs**: Azure ML creates and manages runs
- ✅ **No experiment setting**: Experiment comes from `job.yml`
- ✅ **Direct logging**: All `mlflow.log_param()` and `mlflow.log_metric()` calls work directly

### **Key Code Characteristics:**
```python
# Line 16: Tracking URI is commented out
# mlflow.set_tracking_uri("file:./mlruns")  # Only for local runs

# Lines 34-36: No manual run management
def main(args):
    mlflow.sklearn.autolog()
    # Azure ML automatically manages MLflow runs, so we don't need to start one manually
    run_training_workflow(args)

# Lines 222-224: No experiment setting
# In Azure ML, experiment is automatically set via job.yml
print(f"Azure ML will use experiment from job.yml: {args.experiment_name}")
```

### **Why This Works in Azure ML:**
- Azure ML automatically starts an MLflow run with ID matching the job name
- All MLflow logging calls work within this managed run context
- Experiment name comes from `job.yml` configuration
- Results appear in Azure ML Studio under **Metrics** tab

---

## 🏠 **Converting to Local MLflow Mode**

### **⚠️ WARNING: This Will Break Azure ML Jobs**

If you make these changes, submitting to Azure ML will fail with experiment/run ID conflicts.

### **Required Changes to `src/model/train.py`:**

#### **1. Enable Local Tracking URI (Line 16):**
```python
# FOR LOCAL: Uncomment this line
mlflow.set_tracking_uri("file:./mlruns")
```

#### **2. Add Manual Run Management (Lines 34-36):**
```python
def main(args):
    mlflow.sklearn.autolog()
    
    # FOR LOCAL: Manually manage MLflow runs
    with mlflow.start_run():
        run_training_workflow(args)
```

#### **3. Enable Experiment Setting (Lines 222-224):**
```python
# FOR LOCAL: Manually set experiment
try:
    mlflow.set_experiment(args.experiment_name)
    print(f"MLflow Experiment: {args.experiment_name}")
except Exception as e:
    print(f"Warning: Could not set experiment name, using default. Error: {e}")
```

### **Complete Local Configuration:**
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

### **Run Locally:**
```powershell
# Train with local MLflow
python .\src\model\train.py --training_data .\experimentation\data

# Start MLflow UI to view results
mlflow ui
# Open: http://127.0.0.1:5000
```

---

## ❌ **Why Each Configuration Breaks in Wrong Context**

### **Azure ML Configuration Fails Locally:**
```bash
# Error when running locally with Azure ML config:
AttributeError: 'NoneType' object has no attribute 'info'
# Because mlflow.active_run() returns None without manual run management
```

### **Local Configuration Fails in Azure ML:**
```bash
# Error when submitting to Azure ML with local config:
MlflowException: Cannot start run with ID <job_name> because active run ID 
does not match environment run ID. Make sure --experiment-name or 
--experiment-id matches experiment set with set_experiment()
```

**Root Cause**: Azure ML automatically creates runs and sets experiments, but local config tries to create its own, causing ID conflicts.

---

## 🔄 **Step-by-Step Mode Switching**

### **Azure ML → Local MLflow**

#### **Step 1: Modify `train.py` for Local**
```python
# 1. Uncomment tracking URI (line 16)
mlflow.set_tracking_uri("file:./mlruns")

# 2. Add manual run management (lines 34-36)
def main(args):
    mlflow.sklearn.autolog()
    with mlflow.start_run():  # Add this wrapper
        run_training_workflow(args)

# 3. Enable experiment setting (lines 222-224)
mlflow.set_experiment(args.experiment_name)
print(f"MLflow Experiment: {args.experiment_name}")
```

#### **Step 2: Test Locally**
```powershell
python .\src\model\train.py --training_data .\experimentation\data
mlflow ui
```

#### **Step 3: ⚠️ DO NOT Submit to Azure ML**
This configuration will fail if submitted as an Azure ML job.

### **Local MLflow → Azure ML**

#### **Step 1: Revert `train.py` for Azure ML**
```python
# 1. Comment out tracking URI (line 16)
# mlflow.set_tracking_uri("file:./mlruns")  # Only for local runs

# 2. Remove manual run management (lines 34-36)
def main(args):
    mlflow.sklearn.autolog()
    # No with mlflow.start_run(): wrapper
    run_training_workflow(args)

# 3. Disable experiment setting (lines 222-224)
print(f"Azure ML will use experiment from job.yml: {args.experiment_name}")
# No mlflow.set_experiment() call
```

#### **Step 2: Submit to Azure ML**
```powershell
az ml job create \
  --file src/job.yml \
  --resource-group <your-resource-group> \
  --workspace-name <your-workspace-name>
```

#### **Step 3: ⚠️ DO NOT Run Locally**
This configuration will fail if run locally without Azure ML.

---

## 🎯 **Best Practice: Choose One Mode**

### **For Learning/Development:**
- **Use Azure ML Mode** (current configuration)
- Submit jobs to Azure ML for training
- View results in Azure ML Studio
- Learn cloud MLOps practices

### **For Production MLOps:**
- **Use Azure ML Mode** (current configuration)
- Integrate with CI/CD pipelines
- Use Azure ML for model deployment
- Leverage enterprise features

### **For Local Experimentation Only:**
- **Use Local MLflow Mode**
- Quick iteration and debugging
- Local MLflow UI for experiment tracking
- No cloud dependencies

**Recommendation**: Stick with **Azure ML Mode** since you're learning MLOps and want to see metrics in Azure ML Studio! 🚀

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

## GitHub Actions Issues

### Authentication Failed
```bash
# Check if AZURE_CREDENTIALS secret is:
1. Named exactly "AZURE_CREDENTIALS"
2. Contains complete JSON output from service principal creation
3. Service principal has contributor access
```

### Compute Cluster Issues
```bash
# Common issues:
1. Using compute instance instead of cluster
2. Cluster name mismatch in job.yml
3. Cluster not scaling up (check quota limits)
```

### Job Submission Failed
```bash
# Verify in this order:
1. Resource group and workspace names in workflow
2. Data asset registration
3. Compute cluster status
4. Service principal permissions
```

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

1. ✅ **Set up GitHub Actions**:
   - Create and configure service principal
   - Set up GitHub secrets
   - Configure compute cluster

2. ✅ **Manage Azure Resources**:
   - Register data assets in Azure ML
   - Configure compute options (cluster/instance)
   - Monitor resource usage and costs

3. ✅ **Submit Training Jobs** via:
   - GitHub Actions (recommended)
   - Azure CLI (alternative)
   - Local MLflow (development)

4. ✅ **Monitor and Track**:
   - GitHub Actions workflow runs
   - Azure ML Studio jobs
   - MLflow experiments and metrics

5. ✅ **Switch Between Modes**:
   - GitHub Actions workflow
   - Direct Azure ML submission
   - Local MLflow development

**Congratulations!** You've implemented a complete MLOps pipeline with Azure Machine Learning! 🚀

## Dependencies

- `pytest>=7.1.2`: Testing framework
- `mlflow>=2.14.1`: Experiment tracking and model management
- `pandas>=2.1.0`: Data manipulation
- `scikit-learn==1.7.0`: Machine learning library
- `autopep8>=2.3.0`: Auto formatting 'autopep8 --in-place --aggressive --aggressive src/model/train.py'

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run existing tests to ensure compatibility
5. Submit a pull request

## License

This project is for educational purposes demonstrating MLOps practices with Azure Machine Learning.