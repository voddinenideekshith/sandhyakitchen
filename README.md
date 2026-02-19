# Multi-Brand Food Ordering AI System

Minimal starter scaffold for a production-ready, scalable multi-brand food ordering system.

Stack
- Frontend: Next.js + Tailwind CSS
- Backend: FastAPI (Python)
- DB: PostgreSQL (Neon) with SQLAlchemy async engine
- Payments: Razorpay (skeleton)
- Hosting target: Azure (Docker / App Service)

Quick start (backend)
1. cd backend
2. python -m venv venv
3. venv\Scripts\activate
4. pip install -r requirements.txt
5. copy .env.example to .env and fill `DATABASE_URL`
6. uvicorn main:app --reload --host 0.0.0.0 --port 8000

Quick start (frontend)
1. cd frontend
2. npm install
3. npm run dev

Git
- Initialize repo: `git init`
- Use separate commits for frontend and backend changes.

See deployed-checklist.md for production deployment checklist.

## Development Setup

Follow these steps to prepare a local development environment.

### Create virtual environment

```bash
python -m venv .venv
```

### Activate

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
# or: .venv\Scripts\activate
```

Mac / Linux:

```bash
source .venv/bin/activate
```

### Install runtime dependencies

From the `backend` folder:

```bash
pip install -r requirements.txt
```

### Install development dependencies

Install tools used for testing, linting and formatting:

```bash
pip install -r dev-requirements.txt
```

### Run tests

Run the test suite (ensure `PYTHONPATH=backend` so tests import backend packages correctly):

Windows PowerShell:

```powershell
$env:PYTHONPATH = 'backend'
pytest -v
```

Mac / Linux:

```bash
PYTHONPATH=backend pytest -v
```

### Run formatting & lint checks

```bash
black .
isort .
flake8 .
```

These commands check and fix code style; run them before commits to keep the repo consistent.
