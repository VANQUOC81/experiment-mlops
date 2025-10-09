# ============================================================
# AZURE ML SCORING SCRIPT FOR MLFLOW MODELS
# ============================================================
# This script acts as a "bridge" between HTTP requests and your ML model.
# 
# WHY DO WE NEED THIS?
# - MLflow models are just the trained algorithm (like a .pkl file)
# - Azure ML needs a script to handle HTTP requests, JSON parsing, and responses
# - This separation allows for error handling, logging, and custom logic
#
# HOW IT WORKS:
# 1. Azure ML starts the container and calls init() once
# 2. For each prediction request, Azure ML calls run() with the JSON data
# 3. The script loads the model, makes predictions, and returns results
# ============================================================

import os
import json
import mlflow
import mlflow.sklearn

def init():
    """
    Initialize the model for inference.
    
    This function is called ONCE when the Azure ML container starts.
    It loads your trained MLflow model into memory so it's ready for predictions.
    
    Azure ML automatically sets these environment variables:
    - AZUREML_MODEL_DIR: Path to your registered model files
    - Example: "/var/azureml-app/azureml-models/diabetes-model/10"
    """
    global model
    
    try:
        # Get the model directory from Azure ML environment variable
        # AZUREML_MODEL_DIR points to: /var/azureml-app/azureml-models/diabetes-model/10
        model_base_dir = os.getenv('AZUREML_MODEL_DIR')
        
        if not model_base_dir:
            raise ValueError("AZUREML_MODEL_DIR environment variable is not set!")
        
        # MLflow models are stored in a subdirectory called "model"
        # So the full path becomes: /var/azureml-app/azureml-models/diabetes-model/10/model
        model_path = os.path.join(model_base_dir, 'model')
        
        print(f"Loading model from: {model_path}")
        
        # Check if the model directory exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model directory not found: {model_path}")
        
        print(f"Available files: {os.listdir(model_path)}")
        
        # Load the MLflow model using mlflow.sklearn.load_model()
        # This loads the trained scikit-learn model that was saved during training
        model = mlflow.sklearn.load_model(model_path)
        
        # Validate that the model was loaded successfully
        if model is None:
            raise ValueError("Model loaded but is None!")
        
        print(f"✅ Model loaded successfully!")
        print(f"Model type: {type(model)}")
        print(f"Model features: {model.feature_names_in_ if hasattr(model, 'feature_names_in_') else 'Unknown'}")
        
        # Test the model with a dummy prediction to ensure it's working
        if hasattr(model, 'predict'):
            print("Testing model with dummy data...")
            dummy_data = [[0] * 8]  # 8 features for diabetes model
            test_prediction = model.predict(dummy_data)
            print(f"✅ Model test prediction successful: {test_prediction}")
        else:
            print("⚠️ Warning: Model doesn't have predict method!")
            
    except Exception as e:
        error_msg = f"Failed to initialize model: {str(e)}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg) from e

def run(raw_data):
    """
    Make predictions using the loaded model.
    
    This function is called for EACH prediction request sent to your endpoint.
    It receives the JSON data, processes it, and returns predictions.
    
    Args:
        raw_data: JSON string containing input data in this format:
        {
            "input_data": {
                "columns": ["Pregnancies", "PlasmaGlucose", ...],
                "data": [[9, 104, 51, 7, 24, 27.36983156, 1.350472047, 43], ...]
            }
        }
        
    Returns:
        JSON string containing predictions:
        {"predictions": [0, 1, 0]}  # 0 = No diabetes, 1 = Diabetes
    """
    try:
        # Check if model is loaded
        if 'model' not in globals() or model is None:
            raise RuntimeError("Model not initialized! Call init() first.")
        
        print(f"Received prediction request: {raw_data[:200]}...")  # Log first 200 chars
        
        # Step 1: Parse the JSON input data
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        
        # Step 2: Validate input data structure
        if 'input_data' not in data:
            raise ValueError("Missing 'input_data' key in request")
        
        if 'data' not in data['input_data']:
            raise ValueError("Missing 'data' key in input_data")
        
        input_data = data['input_data']['data']
        
        # Step 3: Validate input data format
        if not isinstance(input_data, list):
            raise ValueError("Input data must be a list")
        
        if not input_data:
            raise ValueError("Input data cannot be empty")
        
        # Check that each row has the expected number of features (8 for diabetes model)
        expected_features = 8
        for i, row in enumerate(input_data):
            if not isinstance(row, list):
                raise ValueError(f"Row {i} must be a list")
            if len(row) != expected_features:
                raise ValueError(f"Row {i} has {len(row)} features, expected {expected_features}")
        
        print(f"Input data shape: {len(input_data)} samples, {len(input_data[0])} features")
        
        # Step 4: Make predictions using the loaded MLflow model
        # This calls your trained scikit-learn LogisticRegression model
        predictions = model.predict(input_data)
        
        print(f"Predictions: {predictions}")
        
        # Step 5: Validate predictions
        if predictions is None:
            raise ValueError("Model returned None predictions")
        
        # Step 6: Format the response as JSON
        # Convert numpy array to Python list for JSON serialization
        result = {"predictions": predictions.tolist()}
        
        print(f"Returning: {result}")
        return json.dumps(result)
        
    except Exception as e:
        # Handle any errors gracefully and return error information
        error = str(e)
        print(f"❌ Error making predictions: {error}")
        
        # Return error information so the client knows what went wrong
        error_response = {"error": f"Prediction failed: {error}"}
        return json.dumps(error_response)

