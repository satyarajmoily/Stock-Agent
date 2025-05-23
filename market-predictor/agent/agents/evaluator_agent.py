import json
from ..market.stock_fetcher import get_actual_outcome_for_prediction
# Assuming stock_fetcher.py is in market-predictor/agent/market/
# and evaluator_agent.py is in market-predictor/agent/agents/

# Path to the predictions log file, relative to the agent directory or project root
# Assuming the agent is run from the 'agent' directory, or paths are handled accordingly.
# For consistency, let's assume paths are relative to the 'market-predictor' root.
PREDICTIONS_LOG_FILE = "market-predictor/predictions_log.json" 

def evaluate_predictions():
    '''
    Reads predictions from the log file, compares them with (simulated) actual market data,
    and updates their status.
    
    Returns:
        bool: True if evaluations suggest no immediate issues, False otherwise.
              (This is a simplified return for now)
    '''
    print("Evaluating predictions...")
    
    try:
        with open(PREDICTIONS_LOG_FILE, "r+") as f:
            lines = f.readlines()
            f.seek(0) # Go back to the beginning of the file to overwrite
            f.truncate() # Clear the file content before writing updated lines
            
            all_evaluations_ok = True
            updated_entries = []

            if not lines:
                print("No predictions found in the log to evaluate.")
                return True # No predictions, so no failures

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    prediction_entry = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Skipping malformed JSON line: {line} - Error: {e}")
                    # Write back malformed lines as is, or log them separately
                    updated_entries.append(line + "\n") # Keep original malformed line
                    all_evaluations_ok = False # Consider malformed JSON an issue
                    continue

                if prediction_entry.get("status") == "pending":
                    print(f"Evaluating: Input='{prediction_entry.get('input')}', Prediction='{prediction_entry.get('prediction')}'")
                    
                    # Fetch actual market outcome using stock_fetcher
                    actual_outcome = get_actual_outcome_for_prediction(
                        prediction_input_summary=prediction_entry.get("input", ""),
                        prediction_timestamp_str=prediction_entry.get("timestamp", "")
                    )
                    print(f"  -> Actual Outcome (simulated by stock_fetcher): {actual_outcome}")

                    # Compare prediction with actual outcome
                    # The current dummy predictor.py and stock_fetcher.py return simple "up"/"down" strings.
                    if prediction_entry.get("prediction") == actual_outcome:
                        prediction_entry["status"] = "pass"
                        print("  -> Status: pass")
                    else:
                        prediction_entry["status"] = "fail"
                        print("  -> Status: fail")
                        all_evaluations_ok = False 
                    
                    updated_entries.append(json.dumps(prediction_entry) + "\n")
                else:
                    # Keep already evaluated entries as they are
                    updated_entries.append(json.dumps(prediction_entry) + "\n")
            
            # Write updated entries back to the file
            for entry_str in updated_entries:
                f.write(entry_str)

    except FileNotFoundError:
        print(f"Predictions log file not found at {PREDICTIONS_LOG_FILE}.")
        print("Please ensure `predictor.py` has run and created the log.")
        return False # Cannot evaluate if log doesn't exist
    except IOError as e:
        print(f"Error accessing predictions log file {PREDICTIONS_LOG_FILE}: {e}")
        return False

    if all_evaluations_ok:
        print("All pending predictions evaluated successfully and seem correct.")
        return True
    else:
        print("Some predictions were marked as 'fail' or issues encountered.")
        return False

if __name__ == '__main__':
    # Example of how to run the evaluator directly
    # This assumes `predictions_log.json` exists in the parent of 'agent' directory
    # To run this directly for testing:
    # Ensure `market-predictor/predictions_log.json` has 'pending' entries.
    # You might need to adjust PREDICTIONS_LOG_FILE if running this file directly
    # vs. running it via agent/main.py
    print("Running evaluator_agent.py directly for testing...")
    # For direct execution, adjust path or ensure CWD is market-predictor
    # PREDICTIONS_LOG_FILE = "../predictions_log.json" # If running from agent/agents/
    
    # To make it runnable from market-predictor/agent/agents path:
    import os
    # Construct path relative to this file's location to reach project root, then to the log
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    PREDICTIONS_LOG_FILE = os.path.join(project_root, "predictions_log.json")
    print(f"Using log file: {PREDICTIONS_LOG_FILE}")

    result = evaluate_predictions()
    print(f"Evaluation result: {'OK' if result else 'Issues Found'}")
