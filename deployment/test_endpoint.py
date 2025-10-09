#!/usr/bin/env python3
"""
============================================================
ENDPOINT TESTING SCRIPT
============================================================
This script tests the deployed diabetes prediction endpoint
in Azure Machine Learning.

Usage:
    python deployment/test_endpoint.py \
        --scoring-uri <endpoint-url> \
        --primary-key <api-key>

You can get the scoring URI and primary key from:
1. Azure ML Studio: Endpoints → Your Endpoint → Consume tab
2. GitHub Actions: Check the deployment workflow output
3. Azure CLI: az ml online-endpoint show and get-credentials

The script sends sample patient data and receives predictions
about diabetes risk (0 = no diabetes, 1 = diabetes).
============================================================
"""

import requests
import json
import argparse
import sys


def test_endpoint(scoring_uri, primary_key, test_data=None):
    """
    Test the diabetes prediction endpoint with sample data.
    
    Args:
        scoring_uri (str): The scoring URI of the endpoint
                          (e.g., https://diabetes-prediction-endpoint.westus2.inference.ml.azure.com/score)
        primary_key (str): The primary key for authentication
        test_data (dict): Test data to send, or None to use default
        
    Returns:
        bool: True if test passed, False otherwise
    """
    
    if test_data is None:
        # Default test data from the Microsoft Learn challenge
        # These are real patient feature values
        test_data = {
            "input_data": {
                "columns": [
                    "Pregnancies",           # Number of pregnancies
                    "PlasmaGlucose",         # Plasma glucose concentration
                    "DiastolicBloodPressure",# Diastolic blood pressure (mm Hg)
                    "TricepsThickness",      # Triceps skin fold thickness (mm)
                    "SerumInsulin",          # 2-Hour serum insulin (mu U/ml)
                    "BMI",                   # Body mass index (weight in kg/(height in m)^2)
                    "DiabetesPedigree",      # Diabetes pedigree function
                    "Age"                    # Age in years
                ],
                "data": [
                    # Patient 1: 43-year-old with moderate risk factors
                    [9, 104, 51, 7, 24, 27.36983156, 1.350472047, 43],
                    
                    # Patient 2: 75-year-old with lower glucose but older age
                    [6, 73, 61, 35, 24, 18.74367404, 1.074147566, 75],
                    
                    # Patient 3: 59-year-old with higher glucose and BMI
                    [4, 115, 50, 29, 243, 34.69215364, 0.741159926, 59]
                ]
            }
        }
    
    # Prepare HTTP headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {primary_key}"
    }
    
    try:
        print("=" * 60)
        print("🚀 TESTING DIABETES PREDICTION ENDPOINT")
        print("=" * 60)
        print(f"\n📍 Scoring URI: {scoring_uri}")
        print(f"🔑 Using API Key: {primary_key[:20]}...")
        print(f"\n📊 Test Data ({len(test_data['input_data']['data'])} samples):")
        print(json.dumps(test_data, indent=2))
        
        # Make the POST request to the endpoint
        print("\n⏳ Sending request...")
        response = requests.post(
            scoring_uri,
            headers=headers,
            data=json.dumps(test_data),
            timeout=30  # 30 second timeout
        )
        
        print(f"\n📬 Response Status: {response.status_code}")
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Endpoint is working correctly")
            print("=" * 60)
            print("\n📋 Full Response:")
            print(json.dumps(result, indent=2))
            
            # Try to extract and display predictions in a user-friendly way
            if isinstance(result, list):
                # If result is a simple list of predictions
                predictions = result
                print(f"\n🎯 Predictions for {len(predictions)} patients:")
                for i, pred in enumerate(predictions):
                    risk = "High Risk (Diabetic)" if pred == 1 else "Low Risk (Not Diabetic)"
                    print(f"   Patient {i+1}: {pred} → {risk}")
                    
            elif isinstance(result, dict) and "predictions" in result:
                # If result has a 'predictions' key
                predictions = result["predictions"]
                print(f"\n🎯 Predictions for {len(predictions)} patients:")
                for i, pred in enumerate(predictions):
                    risk = "High Risk (Diabetic)" if pred == 1 else "Low Risk (Not Diabetic)"
                    print(f"   Patient {i+1}: {pred} → {risk}")
            else:
                print("\n📝 Predictions received (format may vary based on model)")
            
            print("\n" + "=" * 60)
            return True
            
        else:
            # Request failed
            print("\n" + "=" * 60)
            print("❌ ENDPOINT TEST FAILED")
            print("=" * 60)
            print(f"\n🔴 HTTP Status: {response.status_code}")
            print(f"📄 Response Body:\n{response.text}")
            
            # Provide helpful error messages
            if response.status_code == 401:
                print("\n💡 Tip: Check if your primary key is correct")
            elif response.status_code == 404:
                print("\n💡 Tip: Check if the endpoint URL is correct")
            elif response.status_code == 500:
                print("\n💡 Tip: The endpoint may be down or the model may have errors")
            
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out after 30 seconds")
        print("💡 Tip: The endpoint may be cold starting or overloaded")
        return False
        
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection error: {e}")
        print("💡 Tip: Check your internet connection and the endpoint URL")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Failed to parse JSON response: {e}")
        print(f"📄 Raw response:\n{response.text}")
        return False


def load_test_data_from_file(file_path):
    """
    Load test data from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict: Test data loaded from file
        
    Raises:
        Exception: If file cannot be loaded or parsed
    """
    try:
        with open(file_path, 'r') as f:
            test_data = json.load(f)
        print(f"📁 Loaded test data from: {file_path}")
        return test_data
    except FileNotFoundError:
        raise Exception(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in file: {e}")


def main():
    """
    Main function to handle command line arguments and run tests.
    """
    # Set up command line argument parser
    parser = argparse.ArgumentParser(
        description="Test the deployed diabetes prediction endpoint in Azure ML",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="""
Examples:
  # Test with default data
  python src/test_endpoint.py \\
    --scoring-uri https://diabetes-prediction-endpoint.westus2.inference.ml.azure.com/score \\
    --primary-key your-api-key-here
  
  # Test with custom data from file
  python src/test_endpoint.py \\
    --scoring-uri https://diabetes-prediction-endpoint.westus2.inference.ml.azure.com/score \\
    --primary-key your-api-key-here \\
    --test-file my_test_data.json

To get your endpoint credentials:
  1. Go to Azure ML Studio → Endpoints → diabetes-prediction-endpoint
  2. Click on the "Consume" tab
  3. Copy the REST endpoint (scoring URI) and Primary Key
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--scoring-uri",
        required=True,
        help="The scoring URI of the endpoint (get from Azure ML Studio → Endpoints → Consume tab)"
    )
    
    parser.add_argument(
        "--primary-key",
        required=True,
        help="The primary authentication key (get from Azure ML Studio → Endpoints → Consume tab)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--test-file",
        help="Path to JSON file containing custom test data (optional)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Load test data from file if provided
    test_data = None
    if args.test_file:
        try:
            test_data = load_test_data_from_file(args.test_file)
        except Exception as e:
            print(f"❌ Failed to load test file: {e}")
            sys.exit(1)
    
    # Run the endpoint test
    success = test_endpoint(args.scoring_uri, args.primary_key, test_data)
    
    # Exit with appropriate status code
    if success:
        print("\n🎉 All tests passed! Your endpoint is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Test failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()


