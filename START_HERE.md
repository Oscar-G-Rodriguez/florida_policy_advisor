# Start Here (Windows)

This folder is a starter kit for an autonomous build loop using Claude Code.

## What you do
1) Create an empty folder (example):
   C:\Users\<you>\Documents\GitHub\florida_policy_advisor
2) Initialize git in that folder:
   git init
3) Copy the contents of this starter kit into the folder.
4) Verify Claude Code CLI:
   claude --version
5) Run the loop:
   powershell -ExecutionPolicy Bypass -File .\ralph.ps1 -MaxIterations 25

## If you see approval prompts
- Approve the prompt and select the persistent option (Always allow) if offered.
- The allow list in .claude\settings.json aims to reduce prompts, but some environments still ask once.

## When COMPLETE appears
Run:
- python -m pytest
- python -m app.main
Then open:
- http://127.0.0.1:8000
