# Deploy and Test Model

## What Was Created

### Configuration Files
- `src/endpoint.yml` - Endpoint configuration (see file for details)
- `src/deployment.yml` - Deployment configuration (see file for details)
- `src/test_endpoint.py` - Testing script
- `src/sample_test_data.json` - Sample test data

### Workflows
- `.github/workflows/06-train-and-deploy.yml` - **Training + Model Registration**: Trains model and registers it in Azure ML
- `.github/workflows/07-deploy-model.yml` - **Deployment Only**: Deploys already-registered model to endpoint

---

## How to Deploy and Test Model

### Step 1: Deploy the Model

```bash
GitHub → Actions → "Deploy Model to Endpoint" → Run workflow → Select "production" → Run
```

**Duration**: 5-10 minutes

The workflow automatically:
1. Verifies model is already registered (by training workflow)
2. Creates the endpoint
3. Deploys the registered model
4. Tests it

### Step 2: Verify in Azure ML Studio

**Find your endpoint**:
```
https://ml.azure.com → Endpoints → diabetes-prediction-endpoint
```

**Check status**: Should show 🟢 Healthy

### Step 3: Test the Endpoint

**Get credentials**:
```
Azure ML Studio → Endpoints → diabetes-prediction-endpoint → Consume tab
Copy: REST endpoint (scoring URI) and Primary Key
```

**Test with Python**:
```bash
python src/test_endpoint.py \
  --scoring-uri "YOUR_SCORING_URI" \
  --primary-key "YOUR_PRIMARY_KEY"
```

**Or test in Azure ML Studio**:
```
Endpoints → diabetes-prediction-endpoint → Test tab → Paste JSON from sample_test_data.json → Test
```

### Step 4: Success Criteria

- ✅ Model visible in: Azure ML Studio → Models → diabetes-model
- ✅ Endpoint visible in: Azure ML Studio → Endpoints → diabetes-prediction-endpoint
- ✅ GitHub workflow: Green checkmark
- ✅ Test returns predictions: `[0]` or `[1]`

---

## Key Locations in Azure ML Studio

| What | Where |
|------|-------|
| Registered Models | Models → diabetes-model |
| Endpoints | Endpoints → diabetes-prediction-endpoint |
| Test Endpoint | Endpoints → Your Endpoint → **Test tab** |
| Get API Keys | Endpoints → Your Endpoint → **Consume tab** |
| View Logs | Endpoints → Your Endpoint → **Logs tab** |

---

## Test Data Format

```json
{
  "input_data": {
    "columns": ["Pregnancies", "PlasmaGlucose", "DiastolicBloodPressure", "TricepsThickness", "SerumInsulin", "BMI", "DiabetesPedigree", "Age"],
    "data": [[9, 104, 51, 7, 24, 27.36983156, 1.350472047, 43]]
  }
}
```

**Predictions**: `[0]` = Not diabetic, `[1]` = Diabetic

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Model not found in registry" | Run the training workflow first (06-train-and-deploy.yml) - it registers the model |
| 401 Unauthorized | Verify your API key from Azure ML Studio → Consume tab |
| 500 Internal Error | Check logs: Azure ML Studio → Endpoints → Logs tab |
| Deployment takes long | Normal! First deployment takes 5-10 minutes |

## Workflow Separation

**Why two separate workflows?**

| Workflow | Purpose | What it does |
|----------|---------|--------------|
| `06-train-and-deploy.yml` | **Training Pipeline** | 1. Train model on dev data<br/>2. Train model on prod data<br/>3. **Register model** in Azure ML |
| `07-deploy-model.yml` | **Deployment Pipeline** | 1. Verify model is registered<br/>2. Create endpoint<br/>3. Deploy model<br/>4. Test endpoint |

**Benefits of separation:**
- ✅ Can train multiple models before deploying
- ✅ Can deploy same model multiple times
- ✅ Can test different model versions
- ✅ Training and deployment are independent processes

---

## Azure CLI Commands (Optional)

**Check endpoint status**:
```bash
az ml online-endpoint show --name diabetes-prediction-endpoint \
  --resource-group todozi-data-science-rg --workspace-name todozi-ml-ws
```

**Get logs**:
```bash
az ml online-deployment get-logs --name diabetes-deploy-blue \
  --endpoint-name diabetes-prediction-endpoint \
  --resource-group todozi-data-science-rg --workspace-name todozi-ml-ws
```

---

## Clean Up (Optional)

To avoid charges when done testing:
```bash
az ml online-endpoint delete --name diabetes-prediction-endpoint \
  --resource-group todozi-data-science-rg --workspace-name todozi-ml-ws --yes
```

**Cost**: ~$0.19/hour with Standard_DS3_v2 instance

---

## Questions Answered

**Do I need to do anything in Azure ML Studio manually?**
No! Everything is automated via GitHub Actions.

**Do I need to create compute instances for the endpoint?**
No! Azure ML automatically provisions compute based on `instance_type` in `deployment.yml`. This is different from training jobs which use pre-created compute clusters.

**Where do I find the endpoint?**
Azure ML Studio → Endpoints → diabetes-prediction-endpoint

**Do I need Postman to test?**
No! Use the Python script (`test_endpoint.py`) or the Test tab in Azure ML Studio.

---

**That's it! Run the workflow and you're done.** 🚀

