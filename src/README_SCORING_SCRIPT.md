# Azure ML Scoring Script Documentation

This directory contains comprehensive documentation for the Azure ML scoring script (`main.py`) used in managed online endpoint deployments.

## 📁 Files

| File | Purpose |
|------|---------|
| `main.py` | The actual scoring script that handles predictions |
| `main.mermaid` | Complete lifecycle diagram (deployment → requests → shutdown) |
| `main-timeline.mermaid` | Timeline view showing when each phase occurs |
| `main-functions.mermaid` | Detailed function call sequence diagram |

## 🎯 Quick Summary

### What is `main.py`?
A Python script that acts as a "bridge" between HTTP requests and your ML model. It has two main functions:

#### 1. `init()` - Called ONCE during deployment
```python
def init():
    """Load model into memory when container starts"""
    global model
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'model')
    model = mlflow.sklearn.load_model(model_path)
```

**When**: Container startup (deployment phase)  
**Time**: ~5 seconds  
**Purpose**: Load model into RAM for fast predictions  
**Frequency**: Once per deployment

#### 2. `run(raw_data)` - Called for EVERY prediction request
```python
def run(raw_data):
    """Make predictions using the loaded model"""
    data = json.loads(raw_data)
    predictions = model.predict(data['input_data']['data'])
    return json.dumps({"predictions": predictions.tolist()})
```

**When**: Every HTTP POST to /score  
**Time**: ~100ms per request  
**Purpose**: Process data and return predictions  
**Frequency**: Multiple times (hundreds/thousands of requests)

## 📊 Visual Documentation

### 1. Complete Lifecycle Diagram (`main.mermaid`)
Shows the entire process from deployment to shutdown, including:
- Container creation and setup
- Model loading (init)
- Request handling (run)
- Container running state
- Shutdown process

**Key Sections**:
- Phase 1: Deployment (one-time, 2-5 minutes)
- Phase 2: Container Running (continuous)
- Phase 3: Prediction Requests (multiple, ~100ms each)
- Phase 4: Shutdown (when deleted)

### 2. Timeline Diagram (`main-timeline.mermaid`)
Gantt chart showing:
- When each phase occurs
- How long each operation takes
- Parallel operations (container running + handling requests)

**Timing Breakdown**:
- Deployment: ~75-80 seconds (one time)
- Each prediction: ~75-100ms (many times)

### 3. Function Call Flow (`main-functions.mermaid`)
Sequence diagram showing:
- Detailed interaction between components
- Function call order
- Data flow through the system
- How model stays in memory

## 🚀 How It Works

### Deployment Flow
```
Developer → Azure ML → Create Container → Load Model (init) → Ready!
            2-5 minutes                        5 seconds
```

### Prediction Flow
```
Client → HTTP POST → Web Server → run(data) → Model Prediction → Response
                     ~10ms         ~50ms        ~50ms            ~10ms
                                   Total: ~100ms
```

### Key Insight
```
❌ BAD:  Load model → Predict → Unload (5 seconds per request)
✅ GOOD: Load once → Predict → Predict → Predict (100ms per request)
```

## 📈 Performance Impact

| Approach | Time per Request | Reason |
|----------|------------------|--------|
| **Reload model each time** | ~5-10 seconds | Loading .pkl file from disk is slow |
| **Load once in init()** | ~100ms | Model already in RAM, instant access |

**Benefit**: 50-100x faster predictions!

## 🔄 Container Lifecycle

```
┌─────────────────────────────────────────┐
│ DEPLOYMENT (Once)                       │
│ - Create container: 30s                 │
│ - Download model: 30s                   │
│ - Start web server: 5s                  │
│ - Call init(): 5s → Model in RAM       │
│ Total: ~75-80 seconds                   │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ RUNNING STATE (Continuous)              │
│ - Container: Running                    │
│ - Web server: Listening on port 31311  │
│ - Model: Loaded in RAM                  │
│ - Status: Ready for requests            │
│ Duration: Hours/Days/Weeks              │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ HANDLING REQUESTS (Multiple)            │
│ Request 1: run() → 100ms → Response    │
│ Request 2: run() → 100ms → Response    │
│ Request 3: run() → 100ms → Response    │
│ ... thousands of requests ...           │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ SHUTDOWN (When deleted)                 │
│ - Stop web server                       │
│ - Terminate container                   │
│ - Clear memory                          │
└─────────────────────────────────────────┘
```

## 💡 Common Misconceptions

### ❌ WRONG: "The script runs for every prediction"
✅ CORRECT: The container runs continuously, only `run()` is called per request

### ❌ WRONG: "The model is loaded for each request"
✅ CORRECT: Model is loaded ONCE in `init()`, then reused for all requests

### ❌ WRONG: "The web server restarts for each request"
✅ CORRECT: Web server stays running, just processes new requests

## 🔍 Debugging Tips

### Check Deployment Logs
```bash
az ml online-deployment get-logs \
  --name your-deployment \
  --endpoint-name your-endpoint \
  --lines 100
```

**Look for**:
- ✅ "Model loaded successfully!" → init() worked
- ✅ "Predictions: [0 1 0]" → run() is working
- ❌ "Failed to initialize model" → init() failed
- ❌ "Error making predictions" → run() failed

### Common Issues
1. **Container crashes immediately**: init() failed to load model
2. **Slow first request**: Normal (model loading in init())
3. **Slow subsequent requests**: Problem with run() or model size
4. **404 errors**: Endpoint/deployment not ready yet

## 📝 Input/Output Format

### Request Format
```json
{
  "input_data": {
    "columns": ["Pregnancies", "PlasmaGlucose", "DiastolicBloodPressure", 
                "TricepsThickness", "SerumInsulin", "BMI", "DiabetesPedigree", "Age"],
    "data": [
      [9, 104, 51, 7, 24, 27.36983156, 1.350472047, 43],
      [6, 73, 61, 35, 24, 18.74367404, 1.074147566, 75]
    ]
  }
}
```

### Response Format
```json
{
  "predictions": [0, 1]
}
```
Where: `0` = No diabetes, `1` = Has diabetes

## 🔗 Related Files

- `deployment-blue.yml` - References main.py in code_configuration
- `deployment-green.yml` - References main.py for green deployment
- `train.py` - Creates the model that main.py loads
- `../deployment/test_endpoint.py` - Tests the deployed endpoint

## 📚 Further Reading

- [Azure ML Managed Online Endpoints](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-managed-online-endpoints)
- [MLflow Models](https://mlflow.org/docs/latest/models.html)
- [Scoring Script Best Practices](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-advanced-entry-script)

---

**Created**: 2025-10-09  
**Purpose**: Documentation for Azure ML scoring script lifecycle  
**Diagrams**: View .mermaid files in a Mermaid viewer or GitHub

