"""
Logic for generating Plotly charts and exporting them to PNG.

Generates various statistics visualizations from the learning graph.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from models import LearningGraph
from storage import StorageManager


class StatisticsEngine:
    """
    Generates statistical visualizations and exports them as PNG files.

    Attributes:
        graph (LearningGraph): The learning graph to analyze.
        storage_manager (StorageManager): For export directory management.
    """

    def __init__(self, graph: LearningGraph, storage_manager: StorageManager):
        """
        Initialize the StatisticsEngine.

        Args:
            graph (LearningGraph): The learning graph.
            storage_manager (StorageManager): The storage manager.
        """
        self.logger = logging.getLogger(__name__)
        self.graph = graph
        self.storage_manager = storage_manager

    def generate_all_charts(self) -> None:
        """Generate all available statistical charts and export them."""
        try:
            import plotly.graph_objects as go
        except ImportError:
            self.logger.error("Plotly not installed. Cannot generate charts.")
            raise

        export_dir = self.storage_manager.get_export_directory()

        # Chart 1: Answered vs Unanswered
        self._generate_answered_distribution(export_dir)

        # Chart 2: Nodes created over time
        self._generate_timeline_chart(export_dir)

        # Chart 3: Graph connectivity
        self._generate_connectivity_chart(export_dir)

        self.logger.info(f"All charts exported to {export_dir}")

    def _generate_answered_distribution(self, export_dir: Path) -> None:
        """
        Generate a pie chart of answered vs unanswered nodes.

        Args:
            export_dir (Path): Directory to export the chart.
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            raise

        answered = sum(1 for node in self.graph.nodes.values() if node.is_answered)
        unanswered = len(self.graph.nodes) - answered

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["Answered", "Unanswered"],
                    values=[answered, unanswered],
                    marker=dict(colors=["#90EE90", "#FFB6C1"]),
                )
            ]
        )
        fig.update_layout(title="Answered vs Unanswered Questions")

        file_path = export_dir / "answered_distribution.png"
        fig.write_image(str(file_path))
        self.logger.info(f"Exported: {file_path}")

    def _generate_timeline_chart(self, export_dir: Path) -> None:
        """
        Generate a timeline chart of node creation.

        Args:
            export_dir (Path): Directory to export the chart.
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            raise

        # Bin nodes by upload date
        date_counts: Dict[str, int] = {}
        for node in self.graph.nodes.values():
            date_str = node.upload_date.strftime("%Y-%m-%d")
            date_counts[date_str] = date_counts.get(date_str, 0) + 1

        dates = sorted(date_counts.keys())
        counts = [date_counts[d] for d in dates]

        fig = go.Figure(
            data=[go.Bar(x=dates, y=counts, marker=dict(color="#87CEEB"))]
        )
        fig.update_layout(
            title="Questions Created Over Time",
            xaxis_title="Date",
            yaxis_title="Count",
        )

        file_path = export_dir / "timeline.png"
        fig.write_image(str(file_path))
        self.logger.info(f"Exported: {file_path}")

    def _generate_connectivity_chart(self, export_dir: Path) -> None:
        """
        Generate a scatter chart of node connectivity (in-degree, out-degree).

        Args:
            export_dir (Path): Directory to export the chart.
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            raise

        node_ids = []
        in_degrees = []
        out_degrees = []

        for node_id in self.graph.nodes.keys():
            incoming = len(self.graph.get_incoming_edges(node_id))
            outgoing = len(self.graph.get_outgoing_edges(node_id))

            node_ids.append(node_id[:10])  # Truncate for display
            in_degrees.append(incoming)
            out_degrees.append(outgoing)

        fig = go.Figure(
            data=[
                go.Scatter(
                    x=node_ids,
                    y=in_degrees,
                    mode="markers+lines",
                    name="In-Degree",
                    marker=dict(size=8, color="#FF6B6B"),
                ),
                go.Scatter(
                    x=node_ids,
                    y=out_degrees,
                    mode="markers+lines",
                    name="Out-Degree",
                    marker=dict(size=8, color="#4ECDC4"),
                ),
            ]
        )
        fig.update_layout(
            title="Node Connectivity Analysis",
            xaxis_title="Node ID",
            yaxis_title="Degree",
        )

        file_path = export_dir / "connectivity.png"
        fig.write_image(str(file_path))
        self.logger.info(f"Exported: {file_path}")
