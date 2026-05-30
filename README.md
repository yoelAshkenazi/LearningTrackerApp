# 📈 Learning Progress Tracker

[![PyPI version](https://img.shields.io/pypi/v/learning-tracker-app.svg)](https://pypi.org/project/learning-tracker-app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

A premium, interactive desktop GUI application built in Python (using standard **Tkinter**) to map, visualize, track, and analyze your learning progress. 

Create custom question-concept networks, track when you master items, see incremental snapshots of your growth, and automatically export gorgeous, interactive analytics dashboards.

---

## ✨ Key Features

- **🧠 Interactive Mind Mapping**: Drag and drop nodes, double-click to view details, and draw directed learning dependencies dynamically.
- **🎨 State-of-the-Art Visuals**: 
  - Difficulty-based node shapes (Circular for *Easy*, Rectangular for *Medium*, Triangular for *Hard*, Diamond for *Challenging*, and Star-shaped for *Extreme*).
  - Snapshot-based heatmaps (automatically ranges node colors from light red to light blue depending on when you created them relative to your learning journey).
  - Visual cues like bold checkmark badges on mastered nodes.
- **⏱️ Professional History Engine**: Full multi-level **Undo (`Ctrl+Z`)** and **Redo (`Ctrl+Y`)** operations for all layout, connection, and data updates.
- **📊 Premium Interactive Dashboard**: Generates Plotly-powered charts:
  - Pie chart of answered vs unanswered questions (overall and snapshot-specific).
  - Bar chart timeline of concept creation trends.
  - Scatter-line chart mapping node connectivity (in-degree and out-degree analysis).
  - Fully responsive HTML sidebar-driven multi-dashboard uniting all analytics.
- **📂 Clean File Persistence**: Custom JSON save/load system allowing multiple distinct learning graphs.

---

## 📂 Project Directory Structure

The application has been restructured using the modern Python `src/` layout recommended for robust, conflict-free packaging and publishing:

```text
LearningTrackerApp/
├── src/
│   └── learning_tracker/
│       ├── __init__.py           # Package exports & metadata
│       ├── main.py               # Application launcher and logger init
│       ├── models.py             # Dataclasses (QuestionNode, LearningGraph)
│       ├── storage.py            # JSON I/O and export directories
│       ├── utils.py              # Subgraph traversals & timestamp binning
│       ├── statistics_engine.py  # Plotly dashboards HTML generator
│       ├── gui_main.py           # Main window & toolbars orchestration
│       ├── gui_canvas.py         # Custom canvas with drag, shift-drag cues
│       └── gui_popups.py         # Popups for node details creation/edits
├── pyproject.toml                # Modern PEP 621 packaging metadata
├── LICENSE                       # MIT License
└── README.md                     # Comprehensive product guide
```

---

## 🚀 Installation

You can install the package directly using standard pip tools once published.

### Core GUI Only
To keep dependencies extremely light (GUI runs entirely on built-in standard library tools), run:
```bash
pip install learning-tracker-app
```

### Full Analytical Dashboard Support (Recommended)
To enable generating interactive Plotly dashboards and data reports, install with the `stats` extras:
```bash
pip install learning-tracker-app[stats]
```

---

## 🎮 Running the Application

After installing, run the app directly from your terminal using the custom CLI entry point:
```bash
learning-tracker
```

Alternatively, you can run the package module:
```bash
python -m learning_tracker
```

---

## 🖱️ Quick Controls Cheat Sheet

| Interaction | Action |
| :--- | :--- |
| **Right-Click** on empty canvas | Create a new standalone node |
| **Shift + Left-Click + Drag** from a node to empty canvas | Create a new node and draw a connection to it instantly |
| **Shift + Left-Click + Drag** from a node to another node | Draw a directed edge (learning dependency) |
| **Left-Click** on a node | Open detail editor (view dates, edit question/answers, set difficulty, mark completed) |
| **Left-Click + Drag** on a node | Reposition node on the canvas smoothly |
| `Ctrl + Z` / `Ctrl + Y` | Undo / Redo any action |

---

## 📦 Publishing to PyPI

Here is the quick guide to build and upload your package. Make sure you have `build` and `twine` installed:
```bash
pip install --upgrade build twine
```

### 1. Build the Distribution
Run the build script from the project root folder (where `pyproject.toml` resides):
```bash
python -m build
```
This generates `.tar.gz` (source distribution) and `.whl` (built distribution) packages in the `dist/` directory.

### 2. Verify Your Build
Ensure package descriptions are formatted correctly and metadata matches PyPI rules:
```bash
twine check dist/*
```

### 3. Upload to TestPyPI (Recommended first step)
Verify everything looks correct on the test repository:
```bash
twine upload --repository testpypi dist/*
```

### 4. Upload to Production PyPI
Publish your app to the world!
```bash
twine upload dist/*
```

---

## 📄 License

Distributed under the MIT License. See [LICENSE](file:///c:/Users/yoela/PycharmProjects/LearningGraphTracker/LearningTrackerApp/LICENSE) for more details.
