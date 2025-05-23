from datetime import datetime, timedelta
import random

def fetch_market_data(symbol: str, date_str: str):
    '''
    Simulates fetching market data for a given symbol around a specific date.
    In a real implementation, this would call a stock API (e.g., Yahoo Finance, Alpha Vantage).
    
    Args:
        symbol (str): The stock symbol (e.g., "AAPL", "SPY").
                      Not used in the current dummy version but important for real implementation.
        date_str (str): The date string for which to fetch market data (e.g., from prediction timestamp).
                        The dummy version uses this to make the outcome somewhat deterministic.
    
    Returns:
        str: A simulated market outcome, e.g., "up", "down", "stable".
    '''
    print(f"Simulating fetching market data for symbol '{symbol}' around date '{date_str}'...")
    
    # Dummy logic: make it somewhat predictable based on input for testing with evaluator
    # This is just for simulation. A real API would be needed.
    if "inflation" in symbol.lower() or (date_str and "20" in date_str): # Made up condition
        outcome = "down"
    elif "stable" in symbol.lower() or (date_str and "10" in date_str): # Made up condition
        outcome = "up"
    else:
        outcome = random.choice(["up", "down", "stable"])
        
    print(f"  -> Simulated outcome: {outcome}")
    return outcome

def get_actual_outcome_for_prediction(prediction_input_summary: str, prediction_timestamp_str: str):
    '''
    Higher-level function to determine the actual market outcome based on a prediction's input.
    This might involve parsing the input summary for relevant symbols or keywords.
    
    Args:
        prediction_input_summary (str): The summary text used for the prediction.
        prediction_timestamp_str (str): The timestamp of when the prediction was made.
        
    Returns:
        str: Market outcome ("up", "down", "stable").
    '''
    # Dummy logic: try to extract a "symbol" or keyword from the summary
    # This is highly simplistic. Real implementation would need more robust parsing or context.
    if "fed" in prediction_input_summary.lower() or "rates" in prediction_input_summary.lower():
        symbol_hint = "InterestRateSensitiveIndex" # e.g. TBF, TLT, or broad market
    elif "apple" in prediction_input_summary.lower() or "iphone" in prediction_input_summary.lower():
        symbol_hint = "AAPL"
    else:
        symbol_hint = "GenericMarketIndex" # e.g. SPY

    # Use the prediction timestamp as the relevant date
    # A real system might look at market data for T+1 or some relevant window
    market_date = prediction_timestamp_str 
    
    return fetch_market_data(symbol_hint, market_date)


if __name__ == '__main__':
    print("Running stock_fetcher.py directly for testing...")
    
    # Test fetch_market_data
    test_symbol = "TEST"
    # Simulate a date string like one from datetime.now()
    test_date = str(datetime.now() - timedelta(days=1)) 
    outcome1 = fetch_market_data(test_symbol, test_date)
    print(f"Outcome for {test_symbol} on {test_date}: {outcome1}")

    outcome2 = fetch_market_data("inflation-indicator", "2023-10-20")
    print(f"Outcome for inflation-indicator on 2023-10-20: {outcome2}")

    # Test get_actual_outcome_for_prediction
    summary1 = "Fed talks about possible rate hikes due to inflation."
    timestamp1 = str(datetime.now())
    actual1 = get_actual_outcome_for_prediction(summary1, timestamp1)
    print(f"Actual outcome for summary '{summary1}': {actual1}")

    summary2 = "Apple announces new iPhone, stock expected to react."
    timestamp2 = str(datetime.now())
    actual2 = get_actual_outcome_for_prediction(summary2, timestamp2)
    print(f"Actual outcome for summary '{summary2}': {actual2}")
