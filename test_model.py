import joblib
import os
import sys

MODEL_PATH = r"c:\Users\Dell\OneDrive\Desktop\project_sql\pipeline.pkl"

def test_load():
    print(f"Loading model from {MODEL_PATH}...")
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: {MODEL_PATH} does not exist.")
        return
    try:
        model = joblib.load(MODEL_PATH)
        print(f"Model loaded successfully! Type: {type(model)}")
    except Exception as e:
        print(f"FAIL to load model: {e}")

if __name__ == "__main__":
    test_load()
