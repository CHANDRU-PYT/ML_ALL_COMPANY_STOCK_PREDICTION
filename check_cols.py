import joblib
import pandas as pd

MODEL_PATH = r"c:\Users\Dell\OneDrive\Desktop\project_sql\pipeline.pkl"

def check_cols():
    try:
        model = joblib.load(MODEL_PATH)
        print(f"Model type: {type(model)}")
        # If it's a pipeline, check the first step or the features
        if hasattr(model, 'feature_names_in_'):
            print(f"Features: {model.feature_names_in_}")
        elif hasattr(model, 'named_steps'):
            # try to find features in steps
            for name, step in model.named_steps.items():
                if hasattr(step, 'feature_names_in_'):
                    print(f"Features in {name}: {step.feature_names_in_}")
                    break
        else:
            print("Could not find feature names.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_cols()
