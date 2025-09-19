# Machine Learning Project Rules

## Overall Goal
The primary goal of this project is to build a robust and reproducible machine learning model to solve a specific business problem. Reproducibility and clear documentation are paramount.

## Coding Standards & Best Practices
* All Python code must strictly adhere to PEP 8 standards.
* Use type hints for all function and method signatures.
* Avoid hardcoding file paths; always use relative paths from the project root or use a configuration file.
* Document all functions and classes with clear docstrings explaining purpose, parameters, and returns.

## Data Handling & Preparation
* Data files should be stored exclusively in a `production/data/` directory at the project root.
* Never make destructive changes to the raw data files.
* Use `pandas` for data manipulation and `numpy` for numerical operations.

## Modeling & Training
* When training a model, always use a dedicated `models/` directory for saving and loading.
* Log key metrics (e.g., accuracy, F1-score, loss) to a file or a dedicated logging tool.
* For hyperparameter tuning, always use a library like `scikit-learn` or `optuna`.
* Favor simplicity and interpretability over complexity, unless performance gains are significant.

## Agentic Behavior
* When asked to perform a task, always start by analyzing the relevant project files and dependencies.
* If a file path is provided, use the `read_file` tool to retrieve its contents.
* Before writing or editing code, always check the `requirements.txt` file to ensure the necessary libraries are installed.

## Tooling
* The primary testing framework is `pytest`. When asked to add a test, use `pytest` conventions.
* Dependencies are managed with `pip`. Use `pip install -r requirements.txt` to install dependencies.
* Always use PowerShell for command related tasks.

## Environments
* Always execute commands from an activated virtual environment.

# Agentic Behavior
* When provided with file content within <CONTEXT> tags, assume it is the most current and correct version of the file. Do not perform a redundant read_file tool call unless a step in the plan explicitly requires it.