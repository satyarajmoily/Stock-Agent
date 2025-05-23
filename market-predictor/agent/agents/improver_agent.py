import json
import os
from datetime import datetime # Added for PR timestamp
from ..github.pr_creator import create_github_pr
from ..market.stock_fetcher import get_actual_outcome_for_prediction as fetcher_get_actual # For memory update
# Assuming pr_creator.py is in market-predictor/agent/github/
# Assuming stock_fetcher.py is in market-predictor/agent/market/

PREDICTOR_FILE_PATH = "market-predictor/predictor.py"
PREDICTIONS_LOG_FILE = "market-predictor/predictions_log.json"
MEMORY_FILE_PATH = "market-predictor/agent/memory/failed_cases_memory.json"

def improve_logic_if_needed():
    print("Checking if logic improvement is needed...")
    
    # Load past failures history
    past_failures_history = []
    try:
        with open(MEMORY_FILE_PATH, "r") as mf:
            for line in mf:
                line = line.strip()
                if line:
                    try:
                        past_failures_history.append(json.loads(line))
                    except json.JSONDecodeError:
                        print(f"Skipping malformed line in memory file {MEMORY_FILE_PATH}: {line}")
        if past_failures_history:
            print(f"Loaded {len(past_failures_history)} past failed cases from memory.")
        else:
            print(f"No past failures found in memory file: {MEMORY_FILE_PATH} (or file is empty/new).")
    except FileNotFoundError:
        print(f"Memory file {MEMORY_FILE_PATH} not found. Proceeding without past failures history.")
    except IOError as e:
        print(f"Error reading memory file {MEMORY_FILE_PATH}: {e}. Proceeding without past failures history.")
    
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
    
    # Construct memory section for the prompt
    memory_section = ""
    if past_failures_history:
        memory_section += "\n\n--- Past Failures and Learnings (Consider these in your fix) ---\n"
        # Limit to, say, the last 3-5 relevant past failures to keep prompt size manageable
        recent_failures_to_include = min(len(past_failures_history), 3) 
        for i, entry in enumerate(past_failures_history[-recent_failures_to_include:]):
            memory_section += (
                f"Past Case {i+1}:\n"
                f"  Input: \"{entry.get('input_summary', 'N/A')}\"\n"
                f"  Predicted: \"{entry.get('predicted_outcome', 'N/A')}\"\n"
                f"  Actual: \"{entry.get('actual_outcome', 'N/A')}\"\n"
                f"  LLM Suggestion: \"{entry.get('llm_suggestion_summary', 'N/A')[:150]}...\"\n" # Show snippet
            )
        memory_section += "--- End of Past Failures ---\n"

    prompt = f'''You are an AI engineer. The following prediction code failed:

[input]: "{example_failed_case.get('input')}"
[prediction]: "{example_failed_case.get('prediction')}"
[actual]: "opposite of {example_failed_case.get('prediction')}"

Here is the current logic:
---
{current_logic}
---
{memory_section}
Fix the logic to better handle this case, keeping in mind any relevant past failures listed above.
Only return the new Python function code for predict(summary: str).
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

    # --- Update Failed Case Memory ---
    print(f"\nUpdating failed cases memory at {MEMORY_FILE_PATH}...")
    
    # Re-fetch actual outcome for the failed case to store in memory
    # This is because predictions_log.json might not store the 'actual_outcome' directly with the 'fail' status.
    current_actual_outcome_for_memory = fetcher_get_actual(
        prediction_input_summary=example_failed_case.get("input", ""),
        prediction_timestamp_str=example_failed_case.get("timestamp", "")
    )
    print(f"  Fetched actual outcome for memory: {current_actual_outcome_for_memory}")

    new_memory_entry = {
        "failure_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "original_prediction_timestamp": example_failed_case.get("timestamp", "N/A"),
        "input_summary": example_failed_case.get("input", "N/A"),
        "predicted_outcome": example_failed_case.get("prediction", "N/A"),
        "actual_outcome": current_actual_outcome_for_memory,
        "llm_prompt_snippet": prompt[:300] + "...", # Store a snippet of the prompt used
        "llm_suggestion_summary": simulated_llm_response[:300] + "..." # Store a snippet of the suggestion
    }

    try:
        with open(MEMORY_FILE_PATH, "a") as mf: # Append mode
            mf.write(json.dumps(new_memory_entry) + "\n")
        print(f"Successfully appended new failure to memory: {MEMORY_FILE_PATH}")
    except IOError as e:
        print(f"Error writing to memory file {MEMORY_FILE_PATH}: {e}")
    # --- End of Update Failed Case Memory ---
    
    print("Logic improvement process finished (simulation).")

if __name__ == '__main__':
    print("Running improver_agent.py directly for testing...")
    
    # Standard project root calculation
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Define test file paths using absolute paths for clarity in testing
    # These override the module-level globals for the scope of this test run
    local_predictor_file_path = os.path.join(project_root, "predictor.py")
    local_predictions_log_file = os.path.join(project_root, "predictions_log.json")
    local_memory_file_path = os.path.join(project_root, "agent", "memory", "failed_cases_memory.json")

    # Override global paths for the test execution
    # This ensures that the function being tested uses these specific paths during the test.
    global PREDICTOR_FILE_PATH, PREDICTIONS_LOG_FILE, MEMORY_FILE_PATH
    PREDICTOR_FILE_PATH = local_predictor_file_path
    PREDICTIONS_LOG_FILE = local_predictions_log_file
    MEMORY_FILE_PATH = local_memory_file_path
    
    print(f"Using predictor file: {PREDICTOR_FILE_PATH}")
    print(f"Using predictions log file: {PREDICTIONS_LOG_FILE}")
    print(f"Using memory file: {MEMORY_FILE_PATH}")

    # 1. Ensure predictions log has a "fail" case
    try:
        with open(PREDICTIONS_LOG_FILE, "r+") as f:
            lines = f.readlines()
            found_fail = any('"status": "fail"' in line for line in lines)
            if not found_fail and lines:
                try:
                    first_entry = json.loads(lines[0])
                    first_entry["status"] = "fail" # Mark first as fail
                    lines[0] = json.dumps(first_entry) + "\n"
                    f.seek(0)
                    f.truncate()
                    f.writelines(lines)
                    print(f"Added a dummy 'fail' entry to {PREDICTIONS_LOG_FILE} for testing.")
                except (json.JSONDecodeError, IndexError) as e:
                    print(f"Could not add dummy 'fail' entry to {PREDICTIONS_LOG_FILE}: {e}")
            elif not lines:
                 print(f"{PREDICTIONS_LOG_FILE} is empty. Improver test may not find failed cases.")
    except FileNotFoundError:
        print(f"Predictions log file {PREDICTIONS_LOG_FILE} not found. Cannot create dummy fail entry.")
    except IOError as e:
        print(f"IOError with {PREDICTIONS_LOG_FILE}: {e}")

    # 2. Optionally pre-populate memory file for testing memory loading
    # For a clean test, ensure it's empty or has known content.
    # Let's write one dummy past failure.
    dummy_past_failure = {
        "failure_timestamp": "2023-01-01 10:00:00",
        "original_prediction_timestamp": "2023-01-01 09:00:00",
        "input_summary": "Old news about market crash.",
        "predicted_outcome": "up",
        "actual_outcome": "down",
        "llm_prompt_snippet": "Old prompt snippet...",
        "llm_suggestion_summary": "Old suggestion: if 'crash' in summary_lower: return 'down'",
        "notes": "This was a significant past miss."
    }
    try:
        with open(MEMORY_FILE_PATH, "w") as mf: # "w" to overwrite with known state for test
            mf.write(json.dumps(dummy_past_failure) + "\n")
        print(f"Pre-populated memory file {MEMORY_FILE_PATH} with one dummy past failure for testing.")
    except IOError as e:
        print(f"Error pre-populating memory file {MEMORY_FILE_PATH}: {e}")

    # 3. Call the main function to test
    print("\n--- Calling improve_logic_if_needed() ---")
    improve_logic_if_needed()
    print("--- improve_logic_if_needed() finished ---\n")

    # 4. Read and print memory file content AFTER execution
    print(f"Content of memory file {MEMORY_FILE_PATH} after execution:")
    try:
        with open(MEMORY_FILE_PATH, "r") as mf:
            memory_content_after = mf.read()
            if not memory_content_after.strip():
                print("(Memory file is empty or contains only whitespace)")
            else:
                print(memory_content_after)
    except FileNotFoundError:
        print(f"Memory file {MEMORY_FILE_PATH} not found after execution.")
    except IOError as e:
        print(f"Error reading memory file {MEMORY_FILE_PATH} after execution: {e}")
