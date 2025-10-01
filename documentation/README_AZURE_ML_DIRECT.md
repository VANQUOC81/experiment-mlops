# 🌩️ Azure ML Direct Workflow

> **Alternative Option B**: Manual cloud training via Azure CLI

## 📖 Overview

This workflow allows you to train machine learning models directly in Azure ML using the Azure CLI, without GitHub Actions automation. Perfect for manual experimentation, learning Azure ML concepts, and direct cloud development.

## 🎯 When to Use This Workflow

- **Learning Azure ML** concepts and features
- **Manual experimentation** with cloud resources
- **Direct control** over job submission and monitoring
- **Alternative to GitHub Actions** when automation isn't needed

## Prerequisites

1. **Azure ML Workspace** - Create via Azure Portal
2. **Azure CLI** - 64-bit version with ML extension
3. **Compute Instance** - For running training jobs
4. **Data Assets** - Registered datasets in Azure ML

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

### Edit `src/job-dev.yml`
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
  --file src/job-dev.yml \
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
  --file src/job-dev.yml \
  --resource-group <your-resource-group> \
  --workspace-name <your-workspace-name>
```

### Re-run with Different Parameters
```yaml
# Edit src/job-dev.yml to change:
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

## 🎯 Typical Development Workflow

### 1. Development Phase
```powershell
# Submit job with development data
az ml job create \
  --file src/job-dev.yml \
  --resource-group <your-resource-group> \
  --workspace-name <your-workspace-name>
```

### 2. Parameter Tuning
```yaml
# Edit src/job-dev.yml with different parameters
inputs:
  reg_rate: 0.1  # Try different regularization
```

```powershell
# Submit new job
az ml job create \
  --file src/job-dev.yml \
  --resource-group <your-resource-group> \
  --workspace-name <your-workspace-name>
```

### 3. Production Validation
Option A - Edit existing job-dev.yml:
```yaml
# Edit src/job-dev.yml for production data
inputs:
  training_data:
    path: azureml:diabetes-prod-folder@latest
experiment_name: diabetes-prediction-production
```

Option B - Use dedicated production config:
```powershell
# Use the production-specific job configuration
az ml job create \
  --file src/job-prod.yml \
  --resource-group <your-resource-group> \
  --workspace-name <your-workspace-name>
```

> **Note**: The main GitHub Actions workflow uses separate `job-dev.yml` (dev) and `job-prod.yml` (prod) files for better separation.

```powershell
# Submit production job
az ml job create \
  --file src/job-dev.yml \
  --resource-group <your-resource-group> \
  --workspace-name <your-workspace-name>
```

## 📊 Monitoring and Management

### List Recent Jobs
```powershell
az ml job list \
  --workspace-name <your-workspace-name> \
  --resource-group <your-resource-group> \
  --max-results 10
```

### Get Job Details
```powershell
az ml job show \
  --name <job-name> \
  --workspace-name <your-workspace-name> \
  --resource-group <your-resource-group>
```

### Cancel Running Job
```powershell
az ml job cancel \
  --name <job-name> \
  --workspace-name <your-workspace-name> \
  --resource-group <your-resource-group>
```

### Download Job Outputs
```powershell
az ml job download \
  --name <job-name> \
  --workspace-name <your-workspace-name> \
  --resource-group <your-resource-group> \
  --download-path ./job-outputs
```

## 🛠️ Troubleshooting

### Azure CLI Issues

#### 32-bit vs 64-bit CLI
```powershell
# Check if you have 64-bit CLI
az --version
# Should show: Python (Windows) 3.x.x [MSC v.xxxx 64 bit (AMD64)]

# If shows 32-bit, reinstall:
winget uninstall Microsoft.AzureCLI
winget install Microsoft.AzureCLI
```

#### Missing Dependencies
```powershell
# Install missing Python packages
pip install rpds-py pywin32

# Run pywin32 post-install (if needed)
python Scripts/pywin32_postinstall.py -install
```

#### Authentication Expired
```powershell
# Re-authenticate
az login --scope https://management.azure.com/.default
```

### Job Submission Issues

#### Missing Arguments Error
```powershell
# Always include resource group and workspace
az ml job create \
  --file src/job-dev.yml \
  --resource-group <your-resource-group> \
  --workspace-name <your-workspace-name>
```

#### Compute Instance Not Found
Update `src/job-dev.yml`:
```yaml
compute: azureml:<your-actual-compute-instance-name>
```

#### Data Asset Not Found
```powershell
# Verify data asset exists
az ml data list \
  --workspace-name <your-workspace-name> \
  --resource-group <your-resource-group>
```

### MLflow Issues

#### No Metrics in Azure ML Studio
- Check job logs in Azure ML Studio → **Outputs + logs** tab
- Verify MLflow logging calls in training script
- Ensure autolog is enabled

## 🎯 Best Practices

### 1. Organized Experimentation
```powershell
# Use descriptive experiment names
# Edit job-dev.yml:
experiment_name: diabetes-regularization-tuning
```

### 2. Resource Management
```powershell
# Check compute status before submitting
az ml compute show \
  --name diabetes-compute-instance \
  --workspace-name <your-workspace-name> \
  --resource-group <your-resource-group>
```

### 3. Cost Optimization
- Use compute instances that auto-shutdown when idle
- Monitor job duration and costs
- Clean up unused resources regularly

### 4. Version Control
- Keep job configurations in version control
- Document parameter changes
- Use meaningful job descriptions

## 📊 Expected Results

From Azure ML training you should see:
- **Test Accuracy**: ~78-80%
- **Test AUC**: ~85-87%
- **Model Type**: Logistic Regression with L2 regularization
- **Azure ML Studio**: Detailed metrics, logs, and artifacts

## 🔗 Azure ML Resources

### Useful Commands Reference
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
```

### Azure ML Studio Navigation
1. **Jobs**: View all training runs
2. **Experiments**: Organized experiment tracking
3. **Models**: Registered model artifacts
4. **Data**: Data assets and datasets
5. **Compute**: Compute instances and clusters

## 🔗 Related Documentation

- **Main README.md**: GitHub Actions workflow (recommended for production)
- **README_LOCAL_MLFLOW.md**: Local development workflow
- **Azure ML Documentation**: https://docs.microsoft.com/en-us/azure/machine-learning/

## 🎓 Learning Path

1. **Start Here**: Learn Azure ML concepts with direct CLI control
2. **Next**: Try [README_LOCAL_MLFLOW.md](README_LOCAL_MLFLOW.md) for offline development  
3. **Advanced**: Use [main README.md](README.md) for automated CI/CD pipeline

---

**💡 Tip**: Use this workflow to understand Azure ML fundamentals before moving to automated GitHub Actions workflows!
