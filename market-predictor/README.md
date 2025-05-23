# Market Predictor (`market-predictor`)

This repository contains the core logic for the market prediction system and, in later phases, the agent logic for self-improvement.

## Components (Prediction Logic)

*   `predictor.py`: Contains the primary `predict()` function that generates market predictions based on input summaries, and `log_prediction()` to log these predictions.
*   `predictions_log.json`: A log file where all predictions, their inputs, timestamps, and evaluation statuses (pending, pass, fail) are stored. Each entry is a line-delimited JSON object.
*   `requirements.txt`: Lists Python dependencies for this project.
*   `utils.py`: Optional helper utilities for the predictor.

## Agent Components (to be added in Phase 2 onwards)

*   `agent/main.py`: Entry point for the agent logic.
*   `agent/agents/`: Modules for evaluation and improvement agents.
*   `agent/github/`: GitHub API interaction logic.
*   `agent/market/`: Stock data fetching logic.
*   `agent/news/`: News fetching logic.
*   `agent/config.py` & `agent/.env`: Configuration for the agent.

## Purpose

This repository is a core component of an autonomous agent system designed to:
1.  Fetch financial news.
2.  Make market movement predictions using `predictor.py`.
3.  Log these predictions.
4.  Allow an internal agent (part of this repository) to evaluate these predictions against real market data.
5.  Enable the internal agent to update the prediction logic in `predictor.py` if it's found to be inaccurate, subsequently raising a Pull Request with the improvements.

This system aims for a continuous self-improvement cycle for market prediction, all housed within this unified repository for the prototype phase.
