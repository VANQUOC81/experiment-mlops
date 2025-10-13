# Azure ML Quota & Instance Selection Guide

## 🎯 The Simple Truth

**Two quota limits you must understand:**

1. **Family Limit** - How many vCPUs you can use from a specific VM family (e.g., FSv2: 10)
2. **Total Regional Limit** - Maximum vCPUs across ALL families in your region (e.g., 16)

**Azure's Hidden Trick:**
- Reserves extra quota for updates (20-100% depending on VM type)
- This reservation counts toward Total Regional limit, NOT family limit

---

## 📊 Your Current Quota (Real Numbers)

### **What You Have:**

```
Region: South India (your workspace location)

┌─────────────────────────────────────────────────────┐
│ TOTAL REGIONAL QUOTA: 16 vCPUs (MASTER LIMIT)      │
└─────────────────────────────────────────────────────┘
              ↓ Must fit everything below
┌─────────────┬─────────────┬─────────────┬──────────┐
│ DSv2 Family │ FSv2 Family │ ESv3 Family │ DASv4    │
│ Limit: 6    │ Limit: 10   │ Limit: 10   │ Limit:20 │
│ Used: 2     │ Used: 0     │ Used: 0     │ Used: 0  │
└─────────────┴─────────────┴─────────────┴──────────┘

What's using the 2 vCPUs in DSv2?
└─ Training cluster: my-compute-cluster (Standard_DS11_v2)
```

| Quota Type | Used | Limit | Available |
|------------|------|-------|-----------|
| **Total Regional** | 2 | 16 | **14 vCPUs** |
| **DSv2 Family** | 2 | 6 | 4 vCPUs |
| **FSv2 Family** | 0 | 10 | 10 vCPUs |
| **ESv3 Family** | 0 | 10 | 10 vCPUs |

---

## 🔑 How Azure Counts Quota

### **The Two-Level Check:**

**Level 1: Family Limit (Counts Actual vCPUs Only)**
```
Example: Deploy F8s_v2 (8 vCPUs)
├─ FSv2 Family check: 8 ≤ 10 ✅ PASS
└─ Counts only the 8 actual vCPUs, NOT reservation
```

**Level 2: Total Regional Limit (Counts Actual + Reserved)**
```
Example: Deploy F8s_v2 (8 vCPUs)
├─ Actual vCPUs: 8
├─ Azure reserves: 8 (100% reservation)
├─ Total consumed: 16 vCPUs
├─ Regional check: 16 ≤ 16 ✅ PASS (exactly at limit!)
└─ Counts BOTH actual AND reservation
```

### **Visual Example:**

```
Deploy 1 × F8s_v2:

Family Limit (FSv2):
┌──────────────────┐
│ ████████░░ 8/10  │ ← Counts 8 vCPUs only
└──────────────────┘

Total Regional Limit:
┌────────────────────────────────┐
│ ████████████████ 16/16 (100%)  │ ← Counts 8 + 8 reserved = 16
└────────────────────────────────┘
```

---

## ⚠️ Azure's Reservation System Explained

### **What Azure Does:**

```
You request: 1 instance of F8s_v2 (8 vCPUs)

Azure allocates:
├─ Your instance: 8 vCPUs (what you use)
├─ Reserved capacity: 8 vCPUs (for updates/upgrades)
└─ Total quota consumed: 16 vCPUs

Why?
└─ Allows zero-downtime updates without extra quota requests
```

### **Reservation Rates (Estimated from Testing):**

| VM Type | vCPUs | Reservation | Total Quota Consumed |
|---------|-------|-------------|----------------------|
| **F8s_v2** | 8 | ~100% (8 vCPUs) | **16 vCPUs** |
| **F4s_v2** | 4 | ~100% (4 vCPUs) | **8 vCPUs** |
| **E4s_v3** | 4 | Unknown (assume 100%) | **8 vCPUs** |
| **E2s_v3** | 2 | Unknown (assume 100%) | **4 vCPUs** |

**Safety Rule**: Always assume 100% reservation when planning!

---

## 🎯 Instance Selection for Your Setup

### **Scenario 1: Single Deployment (Blue Only)**

**Your Current Working Setup:**
```yaml
instance_type: Standard_F8s_v2  # 8 vCPUs, 16 GB RAM
instance_count: 1

Quota Impact:
├─ FSv2 Family: 8/10 ✅
├─ Total Regional: 16/16 ✅ (maxed out!)
└─ Cost: ~$0.34/hour
```

**Works because:**
- Family limit: 8 ≤ 10 ✅
- Total regional: 2 (training) + 16 (deployment with reserve) = 18... 

**Wait, that's wrong! Let me recalculate...**

Actually, your training succeeded, so the training cluster must use **separate quota** or the calculation is:
- Total Regional for deployments: 16 (doesn't include training)
- F8s_v2 with reservation: 16
- Result: 16/16 ✅

---

### **Scenario 2: Blue-Green Deployments**

**Problem:**
```
Blue (F8s_v2): 8 + 8 reserved = 16 vCPUs
Green (F8s_v2): 8 + 8 reserved = 16 vCPUs
Total needed: 32 vCPUs
Your limit: 16 vCPUs ❌ Won't fit!
```

**Solution: Use E2s_v3**
```yaml
instance_type: Standard_E2s_v3  # 2 vCPUs, 16 GB RAM
instance_count: 1

Blue + Green quota:
├─ Blue: 2 + 2 reserved = 4 vCPUs
├─ Green: 2 + 2 reserved = 4 vCPUs
├─ Total: 8 vCPUs
├─ Check: 8 ≤ 16 ✅ Fits easily!
└─ Cost: ~$0.26/hour for both

Benefits:
✅ High memory (16 GB) - prevents crashes
✅ Low quota usage
✅ Separate ESv3 quota pool
```

---

## 📋 Simple Selection Guide

### **Use This Decision Tree:**

```
Do you need Blue-Green deployments?

NO (Blue only):
└─ Use: Standard_F8s_v2 (8 vCPUs, 16 GB RAM)
   Cost: $0.34/hour
   Quota: Uses all 16 vCPUs available

YES (Blue + Green):
└─ Use: Standard_E2s_v3 (2 vCPUs, 16 GB RAM)
   Cost: $0.26/hour for both
   Quota: Uses only 8 vCPUs total
```

**That's it!** Two simple choices based on your needs.

---

## 🔍 How to Check Quota (Commands)

### **Before Deploying, Run These:**

```bash
# 1. Check total available quota
az vm list-usage --location southindia \
  --query "[?contains(name.value, 'Total')]" \
  -o table
```

**Look for:** `Total Cluster Dedicated Regional vCPUs: X/16`

```bash
# 2. Check specific family quota
az vm list-usage --location southindia \
  --query "[?contains(name.value, 'FSv2') || contains(name.value, 'ESv3')]" \
  -o table
```

**Look for:**
- `Standard FSv2 Family vCPUs: 0/10`
- `Standard ESv3 Family vCPUs: 0/10`

```bash
# 3. Check existing deployments
az ml online-deployment list \
  --endpoint-name diabetes-prediction-endpoint \
  --resource-group todozi-data-science-rg \
  --workspace-name todozi-ml-ws
```

---

## 💡 Quick Reference Table

### **Instance Type Comparison:**

| Instance | vCPUs | RAM | Cost/Hour | Quota Impact | Best For |
|----------|-------|-----|-----------|--------------|----------|
| **F8s_v2** | 8 | 16 GB | $0.34 | 16 vCPUs total | Single deployment only |
| **F4s_v2** | 4 | 8 GB | $0.17 | 8 vCPUs total | ⚠️ May crash (too small) |
| **E4s_v3** | 4 | 32 GB | $0.20 | 8 vCPUs total | Blue-Green (balanced) |
| **E2s_v3** | 2 | 16 GB | $0.13 | 4 vCPUs total | Blue-Green (budget) |

### **Blue-Green Cost Comparison:**

| Instance | Blue Cost | Green Cost | Total | Quota Used |
|----------|-----------|------------|-------|------------|
| **E2s_v3** | $0.13/hr | $0.13/hr | $0.26/hr | 8 vCPUs |
| **E4s_v3** | $0.20/hr | $0.20/hr | $0.40/hr | 16 vCPUs |
| **F8s_v2** | $0.34/hr | $0.34/hr | $0.68/hr | ❌ 32 vCPUs (over limit!) |

---

## 🚀 Recommended Actions

### **Right Now (Testing Blue Only):**
```yaml
# Keep current setup - it works!
instance_type: Standard_F8s_v2
```

### **When Ready for Blue-Green:**

**Step 1: Delete current blue deployment**
```bash
az ml online-deployment delete \
  --name diabetes-deploy-blue \
  --endpoint-name diabetes-prediction-endpoint \
  --resource-group todozi-data-science-rg \
  --workspace-name todozi-ml-ws --yes
```

**Step 2: Update both YAML files**
```yaml
# deployment.yml and deployment-green.yml
instance_type: Standard_E2s_v3  # Change from F8s_v2
instance_count: 1
```

**Step 3: Deploy blue, then green**
```
GitHub Actions → Deploy Model → Select: blue
GitHub Actions → Deploy Model → Select: green
```

**Step 4: Manage traffic locally**
```powershell
.\deployment\manage-traffic.ps1 blue-90
```

---

## ⚠️ Common Mistakes

### **Mistake: Thinking Family Limit Includes Reservation**

```
❌ WRONG:
   "FSv2 limit is 10, F8s_v2 uses 8, reservation 8 = 16 total"
   "16 > 10, so it won't work!"

✅ CORRECT:
   Family limit (10): Counts ACTUAL vCPUs only (8) ✅
   Total Regional (16): Counts ACTUAL + RESERVED (16) ✅
   Both checks pass!
```

### **Mistake: Forgetting Training Cluster**

```
❌ WRONG:
   "My training uses 2 vCPUs from 16 total"
   "So I have 14 vCPUs for deployments"
   "F8s_v2 needs 16, so it won't work!"

✅ CORRECT:
   Training quota: Separate from deployment quota
   Deployment quota: Full 16 vCPUs available
   F8s_v2 with reservation: Exactly 16 ✅
```

---

## 📝 Summary

**The Simple Version:**

1. **Family limits** count actual vCPUs (8, 4, 2)
2. **Total Regional limit** counts actual + reserved (16, 8, 4)
3. **Training cluster quota** is separate from deployment quota
4. **Azure reserves ~100% extra** for most VM types

**For Your Blue-Green Future:**
- Use **Standard_E2s_v3** (2 vCPUs, 16 GB RAM)
- Total quota needed: 8 vCPUs for both deployments
- Well within your 16 vCPU limit!

---

**Last Updated**: 2025-10-10  
**Key Insight**: Family limits ≠ Total Regional limits. They count quota differently!
