"""
Entry point for the Learning Progress Tracker application.

Initializes the logger, ensures required directories exist, and launches
the Tkinter main loop.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

import tkinter as tk

from .gui_main import LearningTrackerApp
from .storage import StorageManager


def setup_logger():
    """
    Configure the application logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("learning_tracker.log"),
        ],
    )
    return logging.getLogger(__name__)


def main():
    """
    Main entry point. Initializes storage and launches the GUI.

    Ensures data and exports directories exist before starting the app.
    """
    logger = setup_logger()
    logger.info("Starting Learning Progress Tracker")

    try:
        storage_manager = StorageManager()
        storage_manager.ensure_directories_exist()
        logger.info("Directories initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize directories: {e}")
        sys.exit(1)

    root = tk.Tk()
    root.title("Learning Progress Tracker")
    root.geometry("1200x800")

    try:
        app = LearningTrackerApp(root, storage_manager)
        logger.info("GUI initialized successfully")
        root.mainloop()
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
