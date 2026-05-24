"""
Handles JSON I/O, directory creation, and file path resolution.

Manages persistence of the learning graph and ensures required
directories exist for data and exports.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from models import LearningGraph


class StorageManager:
    """
    Manages file I/O and directory structure for the application.

    Attributes:
        data_dir (Path): Directory for storing graph data.
        exports_dir (Path): Directory for exporting statistics.
        default_graph_path (Path): Path to the default graph JSON file.
    """

    def __init__(self, data_dir: str = "data", exports_dir: str = "exports"):
        """
        Initialize the StorageManager.

        Args:
            data_dir (str): Directory name for data storage. Defaults to 'data'.
            exports_dir (str): Directory name for exports. Defaults to 'exports'.
        """
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(data_dir)
        self.exports_dir = Path(exports_dir)
        self.default_graph_path = self.data_dir / "graph.json"

    def ensure_directories_exist(self) -> None:
        """
        Create data and exports directories if they do not exist.

        Raises:
            OSError: If directory creation fails.
        """
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Data directory ensured: {self.data_dir}")
        except OSError as e:
            self.logger.error(f"Failed to create data directory: {e}")
            raise

        try:
            self.exports_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Exports directory ensured: {self.exports_dir}")
        except OSError as e:
            self.logger.error(f"Failed to create exports directory: {e}")
            raise

    def save_graph(self, graph: LearningGraph, file_path: Optional[Path] = None) -> bool:
        """
        Save the learning graph to a JSON file.

        Args:
            graph (LearningGraph): The graph to save.
            file_path (Optional[Path]): Custom file path. Uses default if None.

        Returns:
            bool: True if successful, False otherwise.
        """
        path = file_path or self.default_graph_path

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(graph.to_dict(), f, indent=2)
            self.logger.info(f"Graph saved to {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save graph: {e}")
            return False

    def load_graph(self, file_path: Optional[Path] = None) -> Optional[LearningGraph]:
        """
        Load a learning graph from a JSON file.

        Args:
            file_path (Optional[Path]): Custom file path. Uses default if None.

        Returns:
            Optional[LearningGraph]: Loaded graph or None if load fails.
        """
        path = file_path or self.default_graph_path

        if not path.exists():
            self.logger.info(f"No graph file found at {path}. Creating new graph.")
            return LearningGraph(graph_created_at=datetime.now(), snapshot_counter=1)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            graph = LearningGraph.from_dict(data)
            graph.snapshot_counter += 1
            self.logger.info(f"Graph loaded from {path}. Snapshot counter incremented to {graph.snapshot_counter}")
            # Persist the incremented snapshot counter
            self.save_graph(graph, path)
            return graph
        except Exception as e:
            self.logger.error(f"Failed to load graph: {e}")
            return None

    def get_export_directory(self) -> Path:
        """
        Get or create today's export directory.

        If the directory for today (dd-mm-yy) already exists, appends
        a timestamp to make it unique.

        Returns:
            Path: The export directory for today's exports.
        """
        today = datetime.now().strftime("%d-%m-%y")
        export_dir = self.exports_dir / today

        if not export_dir.exists():
            try:
                export_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created export directory: {export_dir}")
                return export_dir
            except OSError as e:
                self.logger.error(f"Failed to create export directory: {e}")
                raise

        # Directory exists, append timestamp
        timestamp = datetime.now().strftime("%H-%M-%S")
        timestamped_dir = self.exports_dir / f"{today}_{timestamp}"

        try:
            timestamped_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created timestamped export directory: {timestamped_dir}")
            return timestamped_dir
        except OSError as e:
            self.logger.error(f"Failed to create timestamped export directory: {e}")
            raise
