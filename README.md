# Project Name

ourPATHS

---

## Table of Contents

- [General Setup](#general-setup)
- [Commits] (#commits)
- [Frontend Setup](#frontend-setup)
- [Backend Setup](#backend-setup)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## General Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/your-org/your-repo.git
    cd your-repo
    ```
2. 🧰 Prerequisites
Python 3.7+ installed on your system.
Git installed.
Bash (already available on Linux/macOS, Git Bash on Windows).
3. Set Up Python Virtual Environment
We use a venv/ folder in the root directory to isolate dependencies.
MacOS & Linux
`
# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
`
Windows (PowerShell)
`
# Create the virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1
`
4. Install Project Dependencies
Once your virtual environment is activated:
`
# Install from requirements.txt (if exists)
pip install -r requirements.txt

# Install pre-commit
pip install pre-commit
`
5. Install Pre-commit Hooks
`
pre-commit install
`

---

## Commits
After first setting up the repo:
`
pre-commit run --all-files
git add .
git commit -m "feat: xyz"
`

Subsequently:
`
git add .
git
`

Pre-commits
1. ✅ scripts/update_requirements.sh:
- Runs pip freeze and updates requirements.txt.
- Stages the file if there are changes.
2. ✅ black:
- Formats all Python code inside src/ using Black.
- If formatting is needed, the commit is blocked until you git add the changes and re-commit.

If Pre-commit fails then retry:
`
git add .
git commit -m "feat: xyz"
`

---

## Frontend Setup

1. Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2. Install frontend dependencies:
    ```bash
    npm install
    ```
3. Start the development server:
    ```bash
    npm start
    ```

---

## Backend Setup

1. Navigate to the backend directory:
    ```bash
    cd backend
    ```
2. Install backend dependencies:
    ```bash
    npm install
    ```
3. Start the backend server:
    ```bash
    npm run dev
    ```

---

## Environment Variables

Create a `.env` file in both `frontend` and `backend` directories. Example:

```env
REACT_APP_API_URL=http://localhost:5000
```

---

## Running Tests

- Frontend:
  ```bash
  cd frontend
  npm test
  ```
- Backend:
  ```bash
  cd backend
  npm test
  ```

---

## Deployment

Instructions for deploying the application (e.g., to Vercel, Heroku, AWS).

---

## Contributing

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

---

## License
