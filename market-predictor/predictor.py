import json
from datetime import datetime

def predict(summary: str) -> str:
    if "inflation" in summary.lower():
        return "down"
    return "up"

def log_prediction(input_text, prediction):
    log_file = "market-predictor/predictions_log.json" # Updated path
    
    data_to_log = {
        "timestamp": str(datetime.now()),
        "input": input_text,
        "prediction": prediction,
        "status": "pending"
    }
    
    try:
        try:
            with open(log_file, "r") as f:
                # Read existing valid JSON lines
                entries = []
                for line in f:
                    line = line.strip()
                    if line: # Ensure line is not empty
                        entries.append(json.loads(line))
        except FileNotFoundError:
            entries = []
        
        entries.append(data_to_log)
        
        with open(log_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
                
    except IOError as e:
        print(f"Error writing to log file {log_file}: {e}")
        with open("predictor_error.log", "a") as error_f: # Consider placing this log too
            error_f.write(f"Failed to log prediction: {data_to_log}, Error: {e}\n")

if __name__ == '__main__':
    # Example usage:
    test_summary = "The latest report shows rising inflation figures."
    prediction_result = predict(test_summary)
    print(f"Input: '{test_summary}'")
    print(f"Prediction: {prediction_result}")
    # Ensure log_prediction is called with the correct path context
    log_prediction(test_summary, prediction_result) 
    print(f"Prediction logged in market-predictor/predictions_log.json")

    test_summary_2 = "The market seems stable with no major news."
    prediction_result_2 = predict(test_summary_2)
    print(f"Input: '{test_summary_2}'")
    print(f"Prediction: {prediction_result_2}")
    log_prediction(test_summary_2, prediction_result_2)
    print(f"Prediction logged in market-predictor/predictions_log.json")
