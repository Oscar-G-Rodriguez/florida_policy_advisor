You are Claude Code operating inside a local repository.

Mission
- Implement the MVP described in PRD.md.
- Execute tasks in plan.md in order.
- Work autonomously: create files, write code, run tests, fix failures, commit.

Hard constraints
- Do not add any UI input for party affiliation.
- Do not produce persuasive campaign language or messaging.
- Do not process personal data.
- Prefer standard Python libraries and small dependencies.

Workflow rules (RALPH)
1) Read PRD.md and plan.md.
2) Find the first task object in plan.md where "passes": false.
3) Implement only what is needed to satisfy that task.
4) Add or update tests for that task.
5) Run the appropriate tests:
   - unit tests for the module you touched, then
   - python -m pytest
6) If tests fail, debug and fix until tests pass.
7) Update plan.md:
   - set that task's "passes" to true ONLY when its steps are complete and tests pass.
8) Append a short entry to activity.md including:
   - iteration timestamp
   - task id
   - summary of changes
   - test command(s) run and result
9) Make a git commit with message: "task(<task id>): <short description>".
10) Exit with:
   - <promise>COMPLETE</promise> only when ALL tasks in plan.md have passes=true.
   - Otherwise, exit normally.

Implementation guidance
- Use src/ layout.
- Suggested package name: app
  - src/app/main.py for FastAPI entrypoint
  - src/app/data/* for ingestion and features
  - src/app/model/* for training and inference
  - src/app/policy/* for policy library and ranking
  - src/app/web/* for templates/static
- Use SQLite via SQLAlchemy. Store DB under data/app.db (gitignored).
- Keep the UI simple (server-rendered templates are acceptable).
- Provide a clear banner in the UI when the fixture fallback is used.

Commands you may run
- python -m pytest
- python -m app.main
- pip install -e .
- git status / git add / git commit

Stop conditions
- If a task is blocked by an unavailable dataset URL, implement the fixture fallback and document the URL as a TODO in code comments and README, then proceed.
