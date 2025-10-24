# Blue-Green Deployment & Traffic Management Guide

## 🎯 Quick Start

### **Deploy Blue or Green:**
```
GitHub Actions → Deploy Model to Endpoint → Select: blue or green
```

**What happens when you select:**
- **Select "blue"** → Uses `src/deployment-blue.yml` → Creates `diabetes-deploy-blue`
- **Select "green"** → Uses `src/deployment-green.yml` → Creates `diabetes-deploy-green`

### **Manage Traffic (Run LOCALLY):**
```powershell
.\deployment\manage-traffic.ps1 status      # Check current
.\deployment\manage-traffic.ps1 blue-90     # 10% to green
.\deployment\manage-traffic.ps1 green-100   # All to green
```

### **Test Endpoint:**
```powershell
python deployment/test_endpoint.py --scoring-uri "..." --primary-key "..."
```

---

## 📋 How Deployment Files Work

### **Two Deployment Configurations:**

```
src/deployment-blue.yml          → Creates: diabetes-deploy-blue
src/deployment-green.yml    → Creates: diabetes-deploy-green
```

### **Workflow Logic:**

```
GitHub Actions Workflow (03-deploy-model.yml)
                    ↓
           User selects blue or green?
                    ↓
        ┌───────────┴───────────┐
        │                       │
    Select "blue"           Select "green"
        ↓                       ↓
Read src/deployment-blue.yml    Read src/deployment-green.yml
        ↓                       ↓
Create/Update              Create/Update
diabetes-deploy-blue       diabetes-deploy-green
        ↓                       ↓
Set traffic: 100%          Set traffic: 0%
        ↓                       ↓
    Primary deployment     Testing deployment
```

**Key Point**: The workflow reads DIFFERENT YAML files based on your selection!

### **Both Files Contain:**

| Setting | deployment-blue.yml (Blue) | deployment-green.yml (Green) |
|---------|----------------------|------------------------------|
| **Name** | `diabetes-deploy-blue` | `diabetes-deploy-green` |
| **Endpoint** | `diabetes-prediction-endpoint` | `diabetes-prediction-endpoint` (SAME) |
| **Model** | `diabetes-model@latest` | `diabetes-model@latest` |
| **Instance** | `Standard_F8s_v2` | `Standard_F8s_v2` (SAME) |
| **Scoring Script** | `main.py` | `main.py` (SAME) |

**Only difference:** The deployment name (blue vs green)

### **Why Two Files?**

- ✅ **Flexibility** - Can use different model versions or instance sizes
- ✅ **Clarity** - Explicit blue vs green configuration
- ✅ **Safety** - Can't accidentally overwrite existing deployment

**Example - Different Model Versions:**
```yaml
# deployment-blue.yml (stable)
model: azureml:diabetes-model:2  # Pin to version 2

# deployment-green.yml (testing new version)
model: azureml:diabetes-model:3  # Test version 3
```

---

## 💰 Critical: Cost Impact

### **Each Deployment = Separate Instance**

| Scenario | Instances Running | Cost/Hour |
|----------|-------------------|-----------|
| **Blue only** | 1 × F8s_v2 | $0.34 |
| **Blue + Green** | 2 × F8s_v2 | **$0.68** ⚠️ DOUBLE! |

**Important**: Green at 0% traffic still costs money! Delete old deployment after switching.

---

## 🚦 Traffic Management Methods

### **Method 1: PowerShell Script (Recommended) - LOCAL**

```powershell
# From project root: D:\Projects\Github\experiment-mlops

# Check status
.\deployment\manage-traffic.ps1 status

# Traffic shifts
.\deployment\manage-traffic.ps1 blue-90    # 10% to green
.\deployment\manage-traffic.ps1 blue-75    # 25% to green
.\deployment\manage-traffic.ps1 blue-50    # 50/50 split
.\deployment\manage-traffic.ps1 green-100  # All to green
.\deployment\manage-traffic.ps1 blue-100   # Rollback
```

**Commands Available:**
- `status` - Show current traffic allocation
- `blue-100` - All to blue (rollback)
- `blue-90` - 90% blue, 10% green
- `blue-75` - 75% blue, 25% green
- `blue-50` - 50/50 split
- `green-100` - All to green

### **Method 2: Azure CLI - LOCAL**

```bash
az ml online-endpoint update \
  --name diabetes-prediction-endpoint \
  --traffic "diabetes-deploy-blue=90,diabetes-deploy-green=10" \
  --resource-group todozi-data-science-rg \
  --workspace-name todozi-ml-ws
```

### **Method 3: Azure ML Studio UI - BROWSER**

1. Go to: https://ml.azure.com → Endpoints
2. Click: `diabetes-prediction-endpoint`
3. Click: "Update traffic"
4. Adjust sliders → Click "Update"

---

## 🔄 Complete Rollout Example

### **Scenario: Deploy New Model Version**

```
Time 0:00 - Deploy Green (GitHub Actions)
├─ GitHub → Deploy Model → Select: green
├─ Result: Green at 0% traffic
└─ Cost: $0.68/hour (BOTH running!)

Time 0:15 - Test Green Manually (Local)
├─ python deployment/test_endpoint.py ...
└─ Verify: Works correctly

Time 0:30 - Start Traffic Shift (Local)
├─ .\deployment\manage-traffic.ps1 blue-90
├─ Monitor for 30 minutes in Azure ML Studio
└─ Check: Error rates, response times

Time 1:00 - Increase to 25% (Local)
├─ .\deployment\manage-traffic.ps1 blue-75
└─ Monitor for 30 minutes

Time 1:30 - 50/50 Split (Local)
├─ .\deployment\manage-traffic.ps1 blue-50
└─ Monitor for 1 hour

Time 2:30 - Full Switch (Local)
├─ .\deployment\manage-traffic.ps1 green-100
└─ Monitor for 1-2 hours

Time 4:30 - Delete Blue (Local)
├─ az ml online-deployment delete --name diabetes-deploy-blue ...
├─ Cost: Back to $0.34/hour
└─ Green is now the primary deployment

Total Time: ~4-5 hours
Total Extra Cost: ~$1.70
```

---

## 📊 What You See in Azure ML Studio

### **ONE Endpoint with TWO Deployments:**

```
Endpoint: diabetes-prediction-endpoint (ONE URL)
├── diabetes-deploy-blue
│   ├── Status: Running ✅
│   ├── Traffic: 90%
│   ├── Model: diabetes-model:2
│   ├── Instance: 1 × Standard_F8s_v2
│   └── Cost: $0.34/hour
│
└── diabetes-deploy-green
    ├── Status: Running ✅
    ├── Traffic: 10%
    ├── Model: diabetes-model:3
    ├── Instance: 1 × Standard_F8s_v2
    └── Cost: $0.34/hour

TOTAL: $0.68/hour (BOTH instances running!)
```

**Key Points:**
- ✅ ONE endpoint URL (clients don't see blue/green)
- ✅ TWO separate compute instances (each costs money)
- ✅ Traffic routes automatically based on percentage
- ⚠️ DOUBLE cost when both running

---

## 🚨 Emergency Rollback

### **If Issues Detected:**

```powershell
# Immediate rollback (takes seconds)
.\deployment\manage-traffic.ps1 blue-100
```

**When to Rollback:**
- ❌ Error rate > 5%
- ❌ Response time > 2x baseline
- ❌ Model predictions look wrong
- ❌ Customer complaints

---

## 💡 Best Practices

### **1. Monitor Between Each Shift**
```
Shift traffic → Wait 30 min → Check metrics → Next shift
```

### **2. Gradual Rollout**
```
✅ Good: 100% → 90% → 75% → 50% → 0%
❌ Bad:  100% → 0% (risky!)
```

### **3. Delete Old Deployment**
```
After 100% switch + 2 hours monitoring:
→ Delete old deployment to save $0.34/hour
```

### **4. Test Before Shifting Traffic**
```
Deploy green → Test manually → THEN shift traffic
```

---

## ⚠️ Common Mistakes

### **Mistake 1: Leaving Both Running**
```
❌ Blue 100%, Green 0% for days
   Cost: $0.68/hour × 720 hours = $489.60/month WASTED!

✅ Delete green if not using
   Cost: $0.34/hour × 720 hours = $244.80/month
```

### **Mistake 2: No Monitoring**
```
❌ Shift to 100% green and forget
   Risk: Issues affect all customers

✅ Monitor for 1-2 hours after full switch
   Action: Rollback if issues detected
```

### **Mistake 3: Forgetting to Delete**
```
❌ Green 100%, Blue 0% but still running
   Waste: $0.34/hour for nothing

✅ Delete blue immediately after validation
   Savings: $8.16/day
```

---

## 📋 Deployment Checklist

### **Before Deploying Green:**
- ☐ New model trained and registered
- ☐ Blue deployment is healthy
- ☐ Have time to monitor (4-5 hours)
- ☐ Know how to rollback

### **During Rollout:**
- ☐ Deploy green (0% traffic)
- ☐ Test green manually
- ☐ Shift to 10% → monitor 30 min
- ☐ Shift to 25% → monitor 30 min
- ☐ Shift to 50% → monitor 1 hour
- ☐ Shift to 100% → monitor 2 hours

### **After Successful Rollout:**
- ☐ Green stable for 2+ hours
- ☐ No error rate increase
- ☐ Response times normal
- ☐ Delete old blue deployment
- ☐ Verify cost back to $0.34/hour

---

## 🎓 Where to Execute Commands

| Tool | Execute Where | When | Purpose |
|------|--------------|------|---------|
| **GitHub Actions** | ☁️ GitHub website | Deploy blue/green | Create deployments |
| **manage-traffic.ps1** | 🖥️ Local PowerShell | During rollout | Shift traffic |
| **test_endpoint.py** | 🖥️ Local terminal | After deployment | Test endpoint |
| **Azure CLI** | 🖥️ Local terminal | Anytime | Manual control |
| **Azure ML Studio** | 🌐 Web browser | Monitor | Visual interface |

**Key Point**: Traffic management is ALWAYS local, never via GitHub Actions!

---

## 🔍 Monitoring

### **Azure ML Studio:**
1. Endpoints → diabetes-prediction-endpoint → Metrics
2. Watch:
   - Request count per deployment
   - Response time comparison
   - Error rates
   - CPU/Memory usage

### **Compare Deployments:**
```
If green shows:
- Response time > blue + 50ms  → Investigate
- Error rate > blue × 2        → Rollback
- CPU > 80%                    → Resource issue
```

---

## 🎯 Quick Commands Reference

```powershell
# Status check
.\deployment\manage-traffic.ps1 status

# Gradual rollout
.\deployment\manage-traffic.ps1 blue-90     # Start with 10%
.\deployment\manage-traffic.ps1 blue-75     # Increase to 25%
.\deployment\manage-traffic.ps1 blue-50     # 50/50
.\deployment\manage-traffic.ps1 green-100   # Full switch

# Rollback
.\deployment\manage-traffic.ps1 blue-100

# Cleanup
az ml online-deployment delete --name diabetes-deploy-blue \
  --endpoint-name diabetes-prediction-endpoint \
  --resource-group todozi-data-science-rg \
  --workspace-name todozi-ml-ws --yes
```

---

## 📖 Related Documentation

- **DEPLOYMENT_GUIDE.md** - First-time deployment setup
- **src/README_SCORING_SCRIPT.md** - How the scoring script works
- GitHub Actions workflows in `.github/workflows/`

---

**Last Updated**: 2025-10-09  
**Execute**: All traffic commands run LOCALLY on your machine  
**Cost Warning**: Both deployments = DOUBLE the cost - delete promptly!
