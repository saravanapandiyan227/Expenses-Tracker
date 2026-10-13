# Expense Tracker with CI/CD and Docker

> **College DevOps Laboratory Project** — Flask · SQLite · Docker · Jenkins · Ansible · Pytest

---

## 1. Project Title

**Expense Tracker with CI/CD and Docker**

## 2. Project Description

A fully functional personal expense tracking web application built with Python Flask and SQLite, deployed using a complete DevOps pipeline involving Git, GitHub, Jenkins, Docker, Pytest, Ansible, and Docker Volume for persistent storage.

> ⚠️ **Disclaimer**: This is a single-user college DevOps demonstration project. It is **not** a multi-user financial platform and must **not** be used for sensitive financial information without additional authentication, authorization, encryption, and security controls.

---

## 3. Project Objectives

- Build a real expense tracking web application.
- Automate the build, test, and deployment pipeline using Jenkins.
- Package the application in a Docker container.
- Persist SQLite data across container restarts using a Docker Volume.
- Deploy automatically using Ansible.
- Validate the pipeline with Pytest automated tests.

---

## 4. Application Features

| Feature | Description |
|---|---|
| 🏠 Dashboard | Total expenses, monthly totals, today's spending, budget status |
| ➕ Add Expense | Full form with category, payment method, date, description |
| 📋 History | Search, filter by category/month, sort by date/amount |
| ✏️ Edit Expense | Pre-populated update form with validation |
| 🗑️ Delete Expense | POST-based deletion with confirmation |
| 🎯 Budget | Set monthly budget, visual progress bar, 80% warning threshold |
| 📊 Reports | Category breakdown bar chart, monthly summary, averages |

---

## 5. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3.11, Flask 3.0 |
| Database | SQLite (via Docker Volume) |
| Testing | Pytest 8.3 |
| Containerization | Docker (python:3.11-slim) |
| CI/CD | Jenkins (Declarative Pipeline) |
| Deployment | Ansible (community.docker collection) |
| Version Control | Git + GitHub |

---

## 6. Database Schema

### Table: `expenses`

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment primary key |
| title | TEXT NOT NULL | Expense title |
| amount | REAL NOT NULL | Positive amount in ₹ |
| category | TEXT NOT NULL | One of 10 defined categories |
| expense_date | TEXT NOT NULL | Date in YYYY-MM-DD format |
| payment_method | TEXT NOT NULL | Cash, UPI, etc. |
| description | TEXT | Optional notes |
| created_at | TEXT | Timestamp of creation |
| updated_at | TEXT | Timestamp of last update |

### Table: `budgets`

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment primary key |
| monthly_budget | REAL NOT NULL | Budget amount in ₹ |
| updated_at | TEXT | Timestamp of last update |

---

## 7. Application Workflow

```
User
 → Add Expense (form)
 → Flask Backend (validates, stores)
 → SQLite Database (persistent via Docker Volume)
 → Dashboard (live totals)
 → Reports & Budget Summary
```

---

## 8. DevOps Architecture

```
Developer
 → Git Commit
 → GitHub Repository
 → Jenkins CI/CD Pipeline
    ├── Stage 1: Checkout (git pull latest code)
    ├── Stage 2: Build   (docker build -t expense-tracker-ci .)
    ├── Stage 3: Test    (docker run --rm ... pytest)
    ├── Stage 4: Deploy  (ansible-playbook via ansible-docker-lab)
    └── Stage 5: Verify  (confirm container is running)
 → Docker Container: expense-tracker-ansible (port 5003)
 → Flask Application
 → SQLite Database
 → Docker Volume: expense_tracker_data
```

> **Important**: Adding, editing, or deleting expenses through the web application does **NOT** trigger Jenkins. Jenkins is solely responsible for building, testing, and deploying the application image.

---

## 9. Project Structure

```
ExpenseTracker/
├── app.py                    # Flask backend (all routes)
├── test_app.py               # Pytest automated tests
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker image definition
├── Jenkinsfile               # CI/CD pipeline definition
├── .gitignore                # Excludes DB, __pycache__, etc.
├── README.md                 # This file
├── ansible/
│   └── expense-deploy.yml    # Ansible deployment playbook
├── templates/
│   ├── base.html             # Base layout template
│   ├── index.html            # Dashboard
│   ├── add_expense.html      # Add Expense form
│   ├── expenses.html         # Expense history + filters
│   ├── edit_expense.html     # Edit Expense form
│   ├── budget.html           # Budget management
│   └── reports.html          # Expense reports
├── static/
│   ├── style.css             # Global stylesheet
│   └── script.js             # Minimal JS utilities
└── data/
    └── .gitkeep              # Keeps folder in git (DB excluded)
```

---

## 10. Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Running Flask locally |
| pip | latest | Installing dependencies |
| Git | any | Version control |
| Docker Desktop | latest | Building and running containers |
| Jenkins | LTS | CI/CD orchestration |
| Ansible | 2.14+ | Container deployment |

---

## 11. Python Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 12. Run Application Locally

```bash
# From ExpenseTracker/ directory
python app.py
```

Application runs at: **http://localhost:5000**

---

## 13. Run Pytest

```bash
# Run all tests with verbose output
python -m pytest test_app.py -v

# Run with short traceback
python -m pytest test_app.py -v --tb=short
```

All 25+ tests must pass before proceeding to Docker.

---

## 14. Build Docker Image

```bash
docker build -t expense-tracker-ci .
```

Verify the image:
```bash
docker images expense-tracker-ci
```

---

## 15. Create Docker Volume

```bash
docker volume create expense_tracker_data
```

Verify:
```bash
docker volume inspect expense_tracker_data
```

---

## 16. Run Docker Container

```bash
docker run -d \
  --name expense-tracker-ansible \
  -p 5003:5000 \
  -v expense_tracker_data:/app/data \
  --restart unless-stopped \
  expense-tracker-ci
```

View logs:
```bash
docker logs -f expense-tracker-ansible
```

---

## 17. Access the Application

| Environment | URL |
|---|---|
| Local Flask | http://localhost:5000 |
| Docker Container | http://localhost:5003 |
| After Ansible Deploy | http://localhost:5003 |

---

## 18. How Jenkins Performs CI/CD

1. **Checkout**: Jenkins pulls the latest code from GitHub using `checkout scm`.
2. **Build**: `docker build -t expense-tracker-ci .` creates the application image.
3. **Test**: `docker run --rm expense-tracker-ci python -m pytest test_app.py` runs all tests in an isolated container. **Pipeline stops if any test fails.**
4. **Deploy**: Jenkins copies the playbook into the Ansible container and runs `ansible-playbook`.
5. **Verify**: Jenkins confirms the application container is running.

> Jenkins is triggered **manually** or by a GitHub webhook on code push. It is **not** triggered by expense operations in the running application.

---

## 19. How Ansible Deploys the Container

The Ansible playbook (`ansible/expense-deploy.yml`) uses the `community.docker.docker_container` module to:

1. Ensure the `expense_tracker_data` volume exists.
2. Start (or restart) the `expense-tracker-ansible` container.
3. Mount the volume at `/app/data`.
4. Map port `5003:5000`.
5. Set `restart_policy: unless-stopped`.

The playbook is **idempotent** — running it multiple times does not create duplicate containers.

**Manual deployment:**
```bash
# Copy playbook into Ansible container
docker cp ansible/expense-deploy.yml ansible-docker-lab:/expense-deploy.yml

# Run playbook
docker exec ansible-docker-lab ansible-playbook -i /inventory.ini /expense-deploy.yml
```

---

## 20. SQLite Persistence Through Docker Volume

The SQLite database lives at `/app/data/expenses.db` **inside the Docker Volume**, not inside the container filesystem.

```
expense_tracker_data (Docker Volume)
    └── expenses.db   ← All expense and budget data
        ↑
        Mounted at /app/data inside the container
```

**Test persistence:**
```bash
# 1. Add an expense through the UI (http://localhost:5003)
# 2. Stop and remove the container
docker stop expense-tracker-ansible
docker rm expense-tracker-ansible

# 3. Redeploy with Ansible
docker exec ansible-docker-lab ansible-playbook -i /inventory.ini /expense-deploy.yml

# 4. Visit http://localhost:5003 — your expense is still there!
```

> ❌ **Never run `docker volume rm expense_tracker_data`** during normal use. This permanently deletes your database.

---

## 21. Push Code to GitHub

```bash
# Initialize Git (first time only)
cd ExpenseTracker
git init

# Stage all files
git add .

# Initial commit
git commit -m "Initial Expense Tracker CI/CD project"

# Set branch to main
git branch -M main

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/expense-tracker-cicd.git

# Push
git push -u origin main
```

**If remote already exists:**
```bash
# Check current remote
git remote -v

# Update remote URL
git remote set-url origin https://github.com/YOUR_USERNAME/expense-tracker-cicd.git
```

> Do **not** hardcode authentication tokens in the Jenkinsfile. Use Jenkins Credentials Manager.

---

## 22. Common Errors and Solutions

| Error | Cause | Solution |
|---|---|---|
| `docker: Cannot connect to the Docker daemon` | Docker Desktop not running | Start Docker Desktop |
| `port 5003 already in use` | Another container using port 5003 | `docker stop expense-tracker-ansible` then redeploy |
| `ModuleNotFoundError: flask` | Flask not installed | `pip install -r requirements.txt` |
| `sqlite3.OperationalError: no such table` | DB not initialized | Flask auto-initializes on start; ensure `init_db()` is called |
| Ansible: `community.docker not found` | Collection missing | `docker exec ansible-docker-lab ansible-galaxy collection install community.docker` |
| Ansible: `Cannot connect to the Docker daemon` | Docker socket not mounted | Ensure `-v /var/run/docker.sock:/var/run/docker.sock` when starting Ansible container |
| Jenkins: `checkout scm: no SCM configured` | Pipeline not linked to repo | Configure Pipeline → SCM in Jenkins job settings |
| Tests fail with `DB path` errors | Tests using production DB | Tests use `tmp_path` fixture — check `expense_app.DB_PATH` override in fixture |

---

## 23. Future Enhancements

- [ ] Multi-user support with authentication (Flask-Login)
- [ ] Export expenses to CSV/PDF
- [ ] Email budget alerts
- [ ] Recurring expense tracking
- [ ] Data visualization with Chart.js
- [ ] REST API for mobile applications
- [ ] PostgreSQL for production-grade storage
- [ ] HTTPS with Let's Encrypt / Nginx reverse proxy
- [ ] Kubernetes deployment with Helm chart
- [ ] Grafana + Prometheus monitoring dashboard

---

## Demonstrating in College DevOps Lab and Viva

### Setup Checklist
- [ ] Docker Desktop is running
- [ ] Jenkins is running and pipeline is configured
- [ ] Ansible container (`ansible-docker-lab`) is running
- [ ] GitHub repository has the latest code

### Demo Flow (5 minutes)
1. **Show the running application** at http://localhost:5003
2. **Add a new expense** and verify it appears on the dashboard
3. **Set a budget** and show the progress bar
4. **View Reports** — category breakdown and monthly summary
5. **Show the GitHub repository** with Jenkinsfile and Ansible playbook
6. **Trigger the Jenkins pipeline** and narrate each stage
7. **Show the Ansible container** running the playbook
8. **Prove data persistence**: stop container → redeploy → data still present

### Key Viva Points
- **Why Docker?** Eliminates "works on my machine" problem; consistent runtime environment
- **Why Ansible?** Idempotent, declarative infrastructure automation
- **Why Docker Volume?** Container filesystem is ephemeral; volume survives container removal
- **Why Pytest?** Automated validation ensures deployment quality; prevents broken code reaching production
- **Why Jenkins?** Automated CI/CD reduces manual errors and enforces testing before deployment
- **What is idempotent?** Running the Ansible playbook twice produces the same result as running it once

---

*Built with ❤️ for the College DevOps Laboratory — Flask · SQLite · Docker · Jenkins · Ansible · Pytest*
