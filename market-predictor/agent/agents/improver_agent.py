import json
import os
from datetime import datetime # Added for PR timestamp
from ..github.pr_creator import create_github_pr
# Assuming pr_creator.py is in market-predictor/agent/github/

PREDICTOR_FILE_PATH = "market-predictor/predictor.py"
PREDICTIONS_LOG_FILE = "market-predictor/predictions_log.json"

def improve_logic_if_needed():
    print("Checking if logic improvement is needed...")
    
    failed_cases = []
    try:
        with open(PREDICTIONS_LOG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("status") == "fail":
                        failed_cases.append(entry)
                except json.JSONDecodeError:
                    print(f"Skipping malformed line in log: {line}")
                    continue
    except FileNotFoundError:
        print(f"Predictions log file not found at {PREDICTIONS_LOG_FILE}. Cannot determine if improvement is needed.")
        return
    except IOError as e:
        print(f"Error reading predictions log file {PREDICTIONS_LOG_FILE}: {e}")
        return

    if not failed_cases:
        print("No failed predictions found. No improvement needed at this time.")
        return

    print(f"Found {len(failed_cases)} failed prediction(s). Attempting to improve logic...")
    
    example_failed_case = failed_cases[0]
    print(f"Example failed case: Input='{example_failed_case.get('input')}', Predicted='{example_failed_case.get('prediction')}', Actual (implied)='not {example_failed_case.get('prediction')}'")

    current_logic = ""
    try:
        with open(PREDICTOR_FILE_PATH, "r") as f:
            current_logic = f.read()
    except FileNotFoundError:
        print(f"Predictor file not found at {PREDICTOR_FILE_PATH}. Cannot proceed.")
        return
    except IOError as e:
        print(f"Error reading predictor file {PREDICTOR_FILE_PATH}: {e}")
        return
    
    prompt = f'''You are an AI engineer. The following prediction code failed:

[input]: "{example_failed_case.get('input')}"
[prediction]: "{example_failed_case.get('prediction')}"
[actual]: "opposite of {example_failed_case.get('prediction')}"

Here is the current logic:
---
{current_logic}
---

Fix the logic to better handle this case. Only return the new Python function code for predict(summary: str).
Ensure the function is complete and can be directly used to replace the existing predict function.
Do not include example usage or any other text outside the function definition.
'''
    print(f"LLM Prompt (simulated):\n---\n{prompt}\n---")
    
    simulated_llm_response = (
        "def predict(summary: str) -> str:\n"
        "    # Example improved logic based on a hypothetical failure\n"
        "    summary_lower = summary.lower()\n"
        "    if \"inflation\" in summary_lower and \"expected\" in summary_lower:\n"
        "        return \"up\" # If inflation is expected, market might have priced it in\n"
        "    elif \"inflation\" in summary_lower:\n"
        "        return \"down\"\n"
        "    elif \"rates\" in summary_lower and \"hike\" in summary_lower:\n"
        "        return \"down\" # Example for rate hikes\n"
        "    elif \"positive news\" in summary_lower:\n"
        "        return \"up\"\n"
        "    else:\n"
        "        return \"up\" # Default\n"
    )
    print(f"Simulated LLM Response (new predictor.py content):\n---\n{simulated_llm_response}\n---")
    
    # --- Integrate with PR Creator ---
    # Generate PR details based on the failed case and new code
    timestamp_str = datetime.now().strftime("%Y%m%d-%H%M%S") # type: ignore # Add import for datetime if not present
    failed_input_short = example_failed_case.get('input', 'unknown_input')[:50].replace(' ', '_')
    
    branch_name = f"fix/improve-logic-{failed_input_short}-{timestamp_str}"
    pr_title = f"Fix: Improve prediction logic for scenarios like '{example_failed_case.get('input')}'"
    
    pr_body = (
        f"Automated PR to improve `predictor.py` based on a failed prediction case.\n\n"
        f"**Failed Case Details:**\n"
        f"- Input: `{example_failed_case.get('input')}`\n"
        f"- Predicted: `{example_failed_case.get('prediction')}`\n"
        f"- (Implied) Actual: `opposite of {example_failed_case.get('prediction')}` (Note: Actual outcome determination logic is separate)\n\n"
        f"**Proposed Change:**\n"
        f"The attached changes to `predictor.py` are suggested by an LLM to better handle this and similar cases.\n\n"
        f"LLM Prompt used (condensed):\n"
        f"```\n{prompt[:300]}...\n```\n\n" # Show a snippet of the prompt
        f"Please review and merge if appropriate."
    )
    
    # The new code for predictor.py is in `simulated_llm_response`
    new_code_content = simulated_llm_response
    
    print("\nCalling PR creator...")
    # This will call the simulation in pr_creator.py
    create_github_pr(
        branch_name=branch_name,
        title=pr_title,
        body=pr_body,
        new_predictor_code=new_code_content
    )
    # --- End of PR Creator Integration ---
    
    print("Logic improvement process finished (simulation).")

if __name__ == '__main__':
    print("Running improver_agent.py directly for testing...")
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # For direct testing, ensure global paths are overridden if they are different
    # from what the test expects.
    # Here, we are testing the functions which use the global paths, so we
    # must ensure the files are at those global paths relative to where this script is run.
    # The script expects to be in market-predictor/agent/agents/
    # And predictor.py and predictions_log.json in market-predictor/
    
    # To ensure testability, we'll use current global PREDICTIONS_LOG_FILE for the manipulation
    # and assume PREDICTOR_FILE_PATH is also correctly set globally.
    
    # Make sure the test log file is referenced correctly for manipulation
    test_log_file_path = os.path.join(project_root, "predictions_log.json")
    
    print(f"Using predictor file: {os.path.join(project_root, 'predictor.py')}") # PREDICTOR_FILE_PATH should resolve to this
    print(f"Using log file for test setup: {test_log_file_path}") # PREDICTIONS_LOG_FILE should resolve to this

    try:
        with open(test_log_file_path, "r+") as f: # Use explicit path for test setup
            lines = f.readlines()
            found_fail = any('"status": "fail"' in line for line in lines)
            if not found_fail and lines:
                try:
                    first_entry = json.loads(lines[0])
                    first_entry["status"] = "fail"
                    lines[0] = json.dumps(first_entry) + "\n"
                    f.seek(0)
                    f.truncate()
                    f.writelines(lines)
                    print(f"Added a dummy 'fail' entry to {test_log_file_path} for testing.")
                except (json.JSONDecodeError, IndexError) as e:
                    print(f"Could not add dummy 'fail' entry to {test_log_file_path}: {e}")
            elif not lines:
                 print(f"{test_log_file_path} is empty. Improver test may not find failed cases.")
    except FileNotFoundError:
        print(f"Log file {test_log_file_path} not found. Cannot create dummy fail entry for testing.")
    
    # Now call the function, which uses the global paths
    improve_logic_if_needed()
