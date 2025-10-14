# How to Choose VM Instance Type for Azure ML Deployments

## 🎯 The 3-Step Process

### **Step 1: Check Your Quota Limits**

**Azure Portal:**
1. Go to: **Subscriptions** → Your subscription → **Usage + quotas**
2. Filter: **Provider** = `Microsoft.MachineLearningServices`, **Location** = `South India`
3. Look at all the quota limits

**Or via Command Line:**
```bash
az vm list-usage --location southindia -o table
```

**What to look for:**

| Quota Name | Usage/Limit | What This Means |
|------------|-------------|-----------------|
| **Total Cluster Dedicated Regional vCPUs** | 4/16 | Maximum 16 vCPUs total across everything |
| **Standard ESv3 Family vCPUs** | 4/6 | Maximum 6 vCPUs for E-series VMs |
| **Standard FSv2 Family vCPUs** | 0/10 | Maximum 10 vCPUs for F-series VMs |
| **Standard DASv4 Family vCPUs** | 0/20 | Maximum 20 vCPUs for DAS-series VMs |

---

### **Step 2: Find Families with High Limits**

**Look for families with Limit ≥ 12 vCPUs** (these can fit blue-green deployments)

**Example from your portal:**
```
✅ DASv4: 0/20 - Has 20 vCPUs available (GOOD for blue-green!)
✅ FSv2: 0/10 - Has 10 vCPUs available
❌ ESv3: 4/6 - Only 2 vCPUs left (NOT enough)
❌ DSv2: 2/6 - Only 4 vCPUs left (shares with training)
```

---

### **Step 3: Pick a Supported VM from That Family**

Go to [Azure ML VM SKU list](https://learn.microsoft.com/en-us/azure/machine-learning/reference-managed-online-endpoints-vm-sku-list?view=azureml-api-2)

**Find the family you chose, then pick a VM:**

**Example: DASv4 family has 20 vCPUs available**

| VM Name | numberOfCores | For Blue-Green? |
|---------|---------------|-----------------|
| Standard_D2as_v4 | 2 | 2×2×2 = 8 vCPUs ✅ Fits! |
| Standard_D4as_v4 | 4 | 4×2×2 = 16 vCPUs ✅ Fits! |
| Standard_D8as_v4 | 8 | 8×2×2 = 32 vCPUs ❌ Over limit |

**Calculation:** `(numberOfCores × 2 for reservation) × 2 deployments`

---

## 💡 Simple Formula

```
Blue-Green Quota Needed = (VM cores) × 2 × 2

Examples:
├─ 2-core VM: 2 × 2 × 2 = 8 vCPUs needed
├─ 4-core VM: 4 × 2 × 2 = 16 vCPUs needed
└─ 8-core VM: 8 × 2 × 2 = 32 vCPUs needed

Pick a VM where: Quota needed ≤ Family limit
```

---

## 🎯 Quick Recommendation

### **Your Current Situation:**

| Family | Your Limit | Available | Can Fit Blue-Green? |
|--------|------------|-----------|---------------------|
| **ESv3** | 6 | 2 (4 used) | ❌ No - E2s_v3 needs 8 total |
| **FSv2** | 10 | 10 | ✅ Yes - F4s_v2 (needs 8) but may crash |
| **DASv4** | 20+ | 20+ | ✅ Yes - D2as_v4 (needs 8) BEST! |

### **Best Choice: Standard_D2as_v4**

**If DASv4 shows 20 vCPUs available in portal:**

```yaml
# Update deployment.yml and deployment-green.yml to:
instance_type: Standard_D2as_v4  # 2 vCPUs, 8 GB RAM

Why:
✅ 2 cores from Azure ML docs
✅ Blue + Green = 8 vCPUs total (with reservation)
✅ DASv4 has 20 vCPU limit (plenty of room!)
✅ AMD-based (different from Intel, good performance)
✅ Cost: ~$0.10/hour per deployment
```

**Quota check:**
```
Blue: 2 + 2 reserved = 4 vCPUs
Green: 2 + 2 reserved = 4 vCPUs
Total: 8 vCPUs ≤ 20 DASv4 limit ✅
```

---

## 📋 Your Checklist

**Before deploying blue-green:**

1. ☐ Check Azure Portal quotas (South India)
2. ☐ Find family with limit ≥ 12 vCPUs
3. ☐ Go to [Azure ML VM SKU docs](https://learn.microsoft.com/en-us/azure/machine-learning/reference-managed-online-endpoints-vm-sku-list?view=azureml-api-2)
4. ☐ Pick 2-core or 4-core VM from that family
5. ☐ Calculate: cores × 2 × 2 ≤ family limit?
6. ☐ Update deployment.yml and deployment-green.yml
7. ☐ Deploy!

---

## 🔍 Verify DASv4 Quota

**Run this command:**
```bash
az vm list-usage --location southindia \
  --query "[?contains(name.value, 'DASv4')]" \
  -o table
```

**If it shows:**
```
Standard DASv4 Family vCPUs: 0/20
```

**Then use:**
```yaml
instance_type: Standard_D2as_v4
```

**If it shows:**
```
Standard DASv4 Family vCPUs: 0/40
```

**Even better! You can use:**
```yaml
instance_type: Standard_D4as_v4  # More powerful (4 vCPUs)
```

---

## ⚠️ Key Points

1. **Family Limit** (from portal) = How many vCPUs that VM family can use
2. **numberOfCores** (from Azure ML docs) = How many vCPUs ONE instance has
3. **Reservation** = Azure doubles your quota usage (safety assumption: 100%)
4. **Blue-Green** = Need quota for TWO deployments simultaneously

**Simple rule:**
```
Find family with limit ≥ 12
Pick 2-core VM from that family
Deploy blue + green
```

---

## 📝 What to Do Now

1. **Check DASv4 quota** (run command above or check portal)
2. **If DASv4 ≥ 20**: Update YAMLs to `Standard_D2as_v4`
3. **If DASv4 < 12**: Request quota increase for ESv3 (6 → 12)
4. **Deploy**: GitHub Actions → blue, then green

---

**Last Updated**: 2025-10-10  
**Simple Process**: Portal quota → Azure ML docs → Calculate → Deploy!
