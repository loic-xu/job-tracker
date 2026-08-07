# 💼 Job Tracker

A modern, lightweight open-source tool to track your job applications (FastAPI, Chrome Extension, CSV).

---

## 🚀 Local Development (Quickstart)

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Setup & Installation
```bash
# Clone the repository
git clone https://github.com/your-username/job-tracker.git
cd job-tracker

# (Optional) Create a virtual environment
py -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r server/requirements.txt
```

### 3. Enable Git Hooks (`pre-commit` & `pre-push`)
This project uses **Ruff** (linting/formatting), **Mypy** (type checking on commit), and **Pytest** (unit tests on push).

```bash
# Install pre-commit, ruff & mypy
pip install pre-commit ruff mypy

# Enable local Git hooks
py -m pre_commit install
py -m pre_commit install --hook-type pre-push
```

### 4. Run Tests
```bash
pytest tests/ -v
```

---

## 🛠️ Project Architecture

- `server/` : FastAPI REST backend & CSV data access layer.
- `tests/` : Pytest unit test suite.
- `chrome-extension/` : Chrome Extension (Manifest V3).
- `data/` : Local CSV application storage (`utf-8-sig`).
