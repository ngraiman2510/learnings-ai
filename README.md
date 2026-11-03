# learnings-ai

A personal, hands-on learning repository for **Agentic AI**, starting with the
Python fundamentals needed to build, understand, and experiment with AI agents.

The goal is to learn in small steps: write Python, work with APIs and language
models, then build up to agent concepts such as tool use, memory, and evaluation.
This repository is a learning journal, so examples may grow and change as I learn.

## Learning path

1. **Python foundations** — syntax, variables, conditions, loops, collections,
   functions, input validation, and small programs.
2. **Python for AI applications** — modules, environments, HTTP requests, JSON,
   and working with APIs.
3. **Language model basics** — prompts, model APIs, structured outputs, and
   handling responses.
4. **Agent building blocks** — tools, multi-step workflows, state, and memory.
5. **Reliable agents** — testing, evaluation, safety, and deployment.

## What I'm working on

The [`ngr-hands-on/`](./ngr-hands-on/) folder contains the current Python
practice projects:

- [`learn.py`](./ngr-hands-on/learn.py) — a small introduction to loops,
  conditionals, and list comprehensions.
- [`learn.ipynb`](./ngr-hands-on/learn.ipynb) — a notebook for interactive
  Python experiments.
- [`grade_manager.py`](./ngr-hands-on/grade_manager.py) — collects student
  marks, validates input, assigns grades, and calculates summary statistics.
- [`tic_tac_toe.py`](./ngr-hands-on/tic_tac_toe.py) — a command-line game
  practicing lists, functions, loops, and game logic.
- [`requirements.txt`](./ngr-hands-on/requirements.txt) — Python packages
  for API and HTTP experiments.

## Get started

You need Python 3 installed. Check your installation with:

```bash
python3 --version
```

Run an exercise from the repository root:

```bash
python3 ngr-hands-on/learn.py
python3 ngr-hands-on/grade_manager.py
python3 ngr-hands-on/tic_tac_toe.py
```

The current exercises use Python's standard library. When you start working
with the packages listed for API experiments, create a virtual environment and
install them with:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r ngr-hands-on/requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

## Progress

- [x] Start with Python fundamentals and small command-line programs
- [ ] Practice Python modules and API requests
- [ ] Make a first language-model API call
- [ ] Build a small tool-using agent
- [ ] Add tests and evaluate agent behavior

Each project is an opportunity to practice a concept before moving on to the
next step.
