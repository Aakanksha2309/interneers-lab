# Interneers Lab

Welcome to the **Interneers Lab** repository! This serves as a minimal starter kit for learning and experimenting with:
- **Django** (Python)
- **Golang** (Go)
- **React**  (with TypeScript)
- **MongoDB** (via Docker Compose)
- Development environment in **VSCode** (recommended)

**Important:** Use the **same email** you shared during onboarding when configuring Git and related tools. That ensures consistency across all internal systems.

### Project structure

```
backend/
  go/          # Golang backend (see backend/go/README.md)
  python/      # Django (Python) backend (see backend/python/README.md)
frontend/      # React + TypeScript (see frontend/README.md)
```

---

## Table of Contents

1. [Getting Started with Git & Forking](#getting-started-with-git-and-forking)
2. [Prerequisites & where to find them](#prerequisites--where-to-find-them)
3. [Setting up & running](#setting-up--running)
4. [Development Workflow](#development-workflow)
   - [Pushing Your First Change](#pushing-your-first-change)
5. [Making your first change](#making-your-first-change)
6. [Running Tests](#running-tests)
7. [Frontend Setup](#frontend-setup)
8. [Further Reading](#further-reading)

---

## Getting Started with Git and Forking

### 1. Setting up Git and the Repo

1. **Install Git** (if not already):
   - **macOS**: [Homebrew](https://brew.sh/) users can run `brew install git`.
   - **Windows**: Use [Git for Windows](https://gitforwindows.org/).
   - **Linux**: Install via your distro's package manager, e.g., `sudo apt-get install git` (Ubuntu/Debian).

2. **Configure Git** with your name and email:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com" # Use the same email you shared during onboarding
   ```

3. **What is Forking?**

   Forking a repository on GitHub creates your own copy under your GitHub account, where you can make changes independently without affecting the original repo. Later, you can make pull requests to merge changes back if needed.

4. Fork the Rippling/interneers-lab repository (ensure you're in the correct org or your personal GitHub account, as directed).
5. **Clone** your forked repo:
   ```bash
   git clone git@github.com:<YourUsername>/interneers-lab.git
   cd interneers-lab
   ```

## Prerequisites & where to find them

Prerequisites (Python, Go, Node, Docker, etc.) and how to verify your setup are documented in each part of the repo:

- **[backend/python/README.md](backend/python/README.md)** — Python/Django, virtualenv, MongoDB
- **[backend/go/README.md](backend/go/README.md)** — Go, MongoDB
- **[frontend/README.md](frontend/README.md)** — Node, Yarn, React

Use the README for the part you're working on.

---

## Setting up & running

Setup and run instructions live in the domain READMEs:

- **Python backend:** [backend/python/README.md](backend/python/README.md) — venv, dependencies, `runserver`, Docker Compose for MongoDB
- **Go backend:** [backend/go/README.md](backend/go/README.md) — `make setup`, `make build-and-run`, Docker Compose
- **Frontend:** [frontend/README.md](frontend/README.md)

---

## Development Workflow

### Making your first change

Step-by-step tutorials live in the domain READMEs:

- **[backend/python/README.md](backend/python/README.md)** — Django starters (e.g. Hello World, Hello {name} API)
- **[backend/go/README.md](backend/go/README.md)** — Go hello-world and APIs
- **[frontend/README.md](frontend/README.md)** — React hello-world and APIs

### Pushing Your First Change

1. **Stage and commit**:
   ```bash
   git add .
   git commit -m "Your descriptive commit message"
   ```
2. **Push to your forked repo (main branch by default):**
   ```bash
   git push origin main
   ```

---

## Running Tests

See the domain READMEs for how to run tests in each stack:

- [backend/python/README.md](backend/python/README.md)
- [backend/go/README.md](backend/go/README.md)
- [frontend/README.md](frontend/README.md)

---

## Further Reading

Each domain has detailed README with links to relevant docs. In general:

- **Django:** [docs.djangoproject.com](https://docs.djangoproject.com/)
- **React:** [react.dev](https://react.dev/learn)
- **Go:** [go.dev/doc](https://go.dev/doc/)
- **MongoDB:** [docs.mongodb.com](https://docs.mongodb.com/)
- **Docker Compose:** [docs.docker.com/compose](https://docs.docker.com/compose/)
