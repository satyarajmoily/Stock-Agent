import json
from datetime import datetime

def predict(summary: str) -> str:
    if "inflation" in summary.lower():
        return "down"
    return "up"

def log_prediction(input_text, prediction):
    # Ensure the directory exists before trying to write the file.
    # (The worker should handle this, but good to be explicit if possible)
    # For simplicity, we'll assume the worker creates parent dirs.
    log_file = "market-predictor-repo/predictions_log.json"
    
    data_to_log = {
        "timestamp": str(datetime.now()),
        "input": input_text,
        "prediction": prediction,
        "status": "pending"
    }
    
    try:
        # Read existing data
        try:
            with open(log_file, "r") as f:
                entries = [json.loads(line) for line in f if line.strip()]
        except FileNotFoundError:
            entries = []
        
        # Append new data
        entries.append(data_to_log)
        
        # Write all data back
        with open(log_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
                
    except IOError as e:
        print(f"Error writing to log file {log_file}: {e}")
        # Fallback or error handling:
        # For now, just print, but in a real system, might raise or log elsewhere
        with open("predictor_error.log", "a") as error_f:
            error_f.write(f"Failed to log prediction: {data_to_log}, Error: {e}\n")

if __name__ == '__main__':
    # Example usage:
    test_summary = "The latest report shows rising inflation figures."
    prediction_result = predict(test_summary)
    print(f"Input: '{test_summary}'")
    print(f"Prediction: {prediction_result}")
    log_prediction(test_summary, prediction_result)
    print(f"Prediction logged in market-predictor-repo/predictions_log.json")

    test_summary_2 = "The market seems stable with no major news."
    prediction_result_2 = predict(test_summary_2)
    print(f"Input: '{test_summary_2}'")
    print(f"Prediction: {prediction_result_2}")
    log_prediction(test_summary_2, prediction_result_2)
    print(f"Prediction logged in market-predictor-repo/predictions_log.json")
