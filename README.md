# Expense Manager

A simple Flask application for tracking personal expenses.

## Features

- Track daily expenses.
- Categorize expenses.
- View a dashboard with monthly summaries and charts.

## Project Setup

This project uses Python 3.9+ and Flask.

### 1. Create a Virtual Environment

It is recommended to use a virtual environment to manage the project's dependencies.

On macOS and Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:
```bash
py -m venv .venv
.venv\Scripts\activate
```

### 2. Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -e .
```
This command installs the application in "editable" mode and pulls in the necessary dependencies like Flask.

### 3. Initialize the Database

Before running the application for the first time, you need to initialize the database. The application uses SQLite.

Run the following command in your terminal:

```bash
# Make sure your FLASK_APP environment variable is set
export FLASK_APP=app
# For windows cmd: set FLASK_APP=app

# Run the init-db command
flask init-db
```
This will create an `instance/expenses.db` file which will store all the application data. You should see a message "Initialized the database."

### 4. Run the Application

Once the setup is complete, you can run the application's development server:

```bash
python run.py
```

The application will be available at `http://127.0.0.1:5001`.
