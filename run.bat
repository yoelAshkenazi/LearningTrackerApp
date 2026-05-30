@echo off
REM Learning Progress Tracker - Windows Batch Runner
REM Starts the Python application in the local src layout

set PYTHONPATH=src
python -m learning_tracker.main
pause
