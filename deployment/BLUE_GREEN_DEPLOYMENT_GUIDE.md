# Blue-Green Deployment Guide

## 🔵🟢 What is Blue-Green Deployment?

Blue-green deployment is a **zero-downtime deployment strategy** where you maintain two identical production environments:

- **🔵 Blue**: Current production version (stable, serving traffic)
- **🟢 Green**: New version being tested (ready to go live)

## 🎯 Why Use Blue-Green?

### **Benefits:**
- ✅ **Zero downtime**: Users never experience service interruption
- ✅ **Instant rollback**: Switch traffic back in seconds if issues occur
- ✅ **Safe testing**: Test new version with real traffic before full switch
- ✅ **A/B testing**: Compare performance of different versions
- ✅ **Risk reduction**: Validate changes before full deployment

### **Common Use Cases:**
- **Model updates**: Deploy new ML model version safely
- **Code changes**: Update scoring script without downtime
- **Configuration changes**: Modify endpoint settings
- **Performance testing**: Compare response times between versions

## 🚀 Blue-Green Scenario: Model Update

### **Current State (Blue Only)**
```bash
# Your current setup
Endpoint: diabetes-prediction-endpoint
├── Blue deployment (v1.0) → 100% traffic
└── Green deployment → None
```

### **Prerequisites Check**

**Before starting blue-green deployment:**
```bash
# Verify blue deployment exists and is healthy
az ml online-deployment show \
  --name diabetes-deploy-blue \
  --endpoint-name diabetes-prediction-endpoint \
  --resource-group todozi-data-science-rg \
  --workspace-name todozi-ml-ws

# If blue doesn't exist, deploy it first:
# GitHub → Actions → "Deploy Model to Endpoint" → Run workflow
```

### **Step 1: Deploy New Model (Green)**

```bash
# 1. Train new model (creates v2.0)
GitHub → Actions → "Train and Deploy Model" → Run workflow

# 2. Deploy green with new model (0% traffic by default)
az ml online-deployment create \
  --file src/deployment-green.yml \
  --resource-group todozi-data-science-rg \
  --workspace-name todozi-ml-ws

# Wait for deployment to complete (5-10 minutes)
# Check status: az ml online-deployment show --name diabetes-deploy-green --endpoint-name diabetes-prediction-endpoint

# 3. Verify both deployments are healthy before allocating traffic
az ml online-deployment list \
  --endpoint-name diabetes-prediction-endpoint \
  --resource-group todozi-data-science-rg \
  --workspace-name todozi-ml-ws
```

**Result:**
```
Endpoint: diabetes-prediction-endpoint
├── Blue (v1.0) → 100% traffic ✅
└── Green (v2.0) → 0% traffic (ready but not serving)
```

### **Step 2: Test Green with Small Traffic**

```bash
# Move 10% traffic to green for testing
.\deployment\manage-traffic.ps1 blue-90
```

**Result:**
```
Endpoint: diabetes-prediction-endpoint
├── Blue (v1.0) → 90% traffic ✅
└── Green (v2.0) → 10% traffic 🧪 (testing)
```

**What to monitor:**
- ✅ Response times
- ✅ Error rates
- ✅ Prediction accuracy
- ✅ Model performance metrics

### **Step 3A: If Green is Good → Full Switch**

```bash
# Move all traffic to green
.\deployment\manage-traffic.ps1 green-100
```

**Result:**
```
Endpoint: diabetes-prediction-endpoint
├── Blue (v1.0) → 0% traffic (standby)
└── Green (v2.0) → 100% traffic ✅ (new production)
```

### **Step 3B: If Green has Issues → Rollback**

```bash
# Rollback to blue
.\deployment\manage-traffic.ps1 blue-100
```

**Result:**
```
Endpoint: diabetes-prediction-endpoint
├── Blue (v1.0) → 100% traffic ✅ (back to stable)
└── Green (v2.0) → 0% traffic (investigate issues)
```

### **Step 4: Cleanup (Optional)**

```bash
# After confirming green is stable, delete blue
az ml online-deployment delete \
  --name diabetes-deploy-blue \
  --endpoint-name diabetes-prediction-endpoint \
  --resource-group todozi-data-science-rg \
  --workspace-name todozi-ml-ws \
  --yes
```

## 🛠️ How to Use the Traffic Management Script

### **PowerShell Script Usage:**

```powershell
# Show current traffic allocation
.\deployment\manage-traffic.ps1 status

# All traffic to blue (rollback)
.\deployment\manage-traffic.ps1 blue-100

# All traffic to green (full switch)
.\deployment\manage-traffic.ps1 green-100

# Test green with 10% traffic
.\deployment\manage-traffic.ps1 blue-90

# Gradual rollout: 75% blue, 25% green
.\deployment\manage-traffic.ps1 blue-75

# A/B testing: 50/50 split
.\deployment\manage-traffic.ps1 blue-50
```

### **Manual Azure CLI Commands:**

```bash
# Check current status
az ml online-endpoint show \
  --name diabetes-prediction-endpoint \
  --resource-group todozi-data-science-rg \
  --workspace-name todozi-ml-ws \
  --query "traffic"

# Update traffic allocation
az ml online-endpoint update \
  --name diabetes-prediction-endpoint \
  --resource-group todozi-data-science-rg \
  --workspace-name todozi-ml-ws \
  --traffic "diabetes-deploy-blue=90,diabetes-deploy-green=10"
```

## 📊 Traffic Allocation Strategies

### **1. Big Bang (Not Recommended)**
```
Blue: 100% → 0%
Green: 0% → 100%
```
- ❌ High risk
- ❌ No testing with real traffic

### **2. Canary Deployment (Recommended)**
```
Blue: 100% → 90% → 50% → 0%
Green: 0% → 10% → 50% → 100%
```
- ✅ Gradual rollout
- ✅ Risk mitigation
- ✅ Performance validation

### **3. A/B Testing**
```
Blue: 50% (permanent)
Green: 50% (permanent)
```
- ✅ Compare versions
- ✅ Measure performance
- ✅ Data-driven decisions

## 🔍 Monitoring Blue-Green Deployments

### **Key Metrics to Track:**

1. **Response Time**
   ```bash
   # Compare response times
   az ml online-deployment show \
     --name diabetes-deploy-blue \
     --endpoint-name diabetes-prediction-endpoint \
     --query "request_settings"
   ```

2. **Error Rate**
   ```bash
   # Check deployment logs
   az ml online-deployment get-logs \
     --name diabetes-deploy-green \
     --endpoint-name diabetes-prediction-endpoint
   ```

3. **Traffic Distribution**
   ```bash
   # Monitor traffic allocation
   .\deployment\manage-traffic.ps1 status
   ```

### **Azure ML Studio Monitoring:**
- Go to: Endpoints → diabetes-prediction-endpoint
- **Overview tab**: Traffic graphs, request rates
- **Deployments tab**: Individual deployment metrics
- **Logs tab**: Real-time logs from both deployments

## 💰 Cost Considerations

### **Blue-Green Cost Impact:**
- **⚠️ DOUBLE COMPUTE COST** during transition (both deployments running simultaneously)
- **Current Setup**: 2x Standard_DS3_v2 = ~$0.38/hour ($9.12/day, $273.60/month)

### **Cost Breakdown:**
```
Blue (DS3_v2):  $0.19/hour
Green (DS3_v2): $0.19/hour
TOTAL:          $0.38/hour while both running
```

### **Mitigation Strategies:**
  - ✅ Use smaller instance types for testing (`Standard_DS2_v2` = $0.10/hour)
  - ✅ Quick transitions (minutes to hours, not days)
  - ✅ Delete old deployment promptly after successful switch
  - ✅ Only deploy green when ready to test (don't leave it idle)
  - ✅ Use scheduled scaling if supported

### **Cost Optimization:**
```yaml
# For green deployment testing
instance_type: Standard_DS2_v2  # Cheaper option
instance_count: 1
```

## ⚠️ Important Considerations

### **Model Version Pinning:**

**Problem with `@latest`:**
```yaml
# Both deployments use @latest
model: azureml:diabetes-model@latest
```

**Risk**: If you redeploy blue after training a new model, both blue and green will use the same (new) version, defeating the purpose of blue-green!

**Best Practice for Production:**
```yaml
# Blue deployment (stable production)
model: azureml:diabetes-model:1  # Pin to specific version

# Green deployment (testing new version)
model: azureml:diabetes-model:2  # Explicitly specify new version
```

**For Learning/Development**: Using `@latest` is fine for this challenge, but be aware of this limitation in real production environments.

## 🚨 Rollback Scenarios

### **When to Rollback:**
- ❌ Error rate > 5%
- ❌ Response time > 2x baseline
- ❌ Model accuracy drops significantly
- ❌ Business metrics decline

### **Rollback Commands:**
```bash
# Immediate rollback
.\deployment\manage-traffic.ps1 blue-100

# Check if rollback was successful
.\deployment\manage-traffic.ps1 status
```

## 📋 Blue-Green Checklist

### **Before Deployment:**
- [ ] New model trained and registered
- [ ] Green deployment configuration ready
- [ ] Monitoring alerts configured
- [ ] Rollback plan defined
- [ ] Team notified of deployment

### **During Deployment:**
- [ ] Deploy green with 0% traffic
- [ ] Validate green deployment health
- [ ] Start with 10% traffic to green
- [ ] Monitor key metrics
- [ ] Gradually increase green traffic
- [ ] Full switch when confident

### **After Deployment:**
- [ ] Monitor for 24 hours
- [ ] Delete old blue deployment
- [ ] Update documentation
- [ ] Record lessons learned

## 🎯 Best Practices

### **Do:**
- ✅ Always test with small traffic first
- ✅ Monitor closely during transition
- ✅ Have rollback plan ready
- ✅ Document deployment process
- ✅ Use gradual traffic shifts

### **Don't:**
- ❌ Switch 100% traffic immediately
- ❌ Deploy without testing
- ❌ Ignore monitoring alerts
- ❌ Skip rollback preparation
- ❌ Leave old deployments running indefinitely

---

## 🎉 Summary

Blue-green deployment gives you:
- **Safety**: Test before full deployment
- **Speed**: Instant rollback if issues
- **Confidence**: Gradual traffic shifts
- **Zero downtime**: Users never affected

**Your current setup is ready for blue-green!** You just need to:
1. Create `deployment-green.yml` ✅ (Done)
2. Use traffic management script ✅ (Done)
3. Deploy green when you have a new model version

**Next time you update your model, try the blue-green approach!** 🚀
