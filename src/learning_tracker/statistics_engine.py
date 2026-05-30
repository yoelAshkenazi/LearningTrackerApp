"""
Logic for generating Plotly charts and exporting them to PNG.

Generates various statistics visualizations from the learning graph.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from .models import LearningGraph
from .storage import StorageManager


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

        # Chart 1: Answered vs Unanswered (Overall)
        self._generate_answered_distribution(export_dir)

        # Chart 2: Nodes created over time (Overall)
        self._generate_timeline_chart(export_dir)

        # Chart 3: Graph connectivity (Overall)
        self._generate_connectivity_chart(export_dir)

        # Generate snapshot-specific charts for each snapshot
        snapshots: List[int] = []
        if self.graph.nodes:
            snapshots = sorted(list(set(node.snapshot for node in self.graph.nodes.values())))
            for snapshot in snapshots:
                self._generate_answered_distribution(export_dir, snapshot=snapshot)
                self._generate_timeline_chart(export_dir, snapshot=snapshot)
                self._generate_connectivity_chart(export_dir, snapshot=snapshot)

        # Generate premium index dashboard linking them all together!
        self._generate_dashboard(export_dir, snapshots)

        self.logger.info(f"All charts exported to {export_dir}")

    def _generate_answered_distribution(self, export_dir: Path, snapshot: Optional[int] = None) -> None:
        """
        Generate a pie chart of answered vs unanswered nodes.

        Args:
            export_dir (Path): Directory to export the chart.
            snapshot (Optional[int]): If provided, only analyze nodes from this snapshot.
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            raise

        if snapshot is not None:
            nodes = [node for node in self.graph.nodes.values() if node.snapshot == snapshot]
            title = f"Answered vs Unanswered Questions (Snapshot {snapshot})"
            file_name = f"answered_distribution_snapshot_{snapshot}.html"
        else:
            nodes = list(self.graph.nodes.values())
            title = "Answered vs Unanswered Questions"
            file_name = "answered_distribution.html"

        if not nodes:
            self.logger.warning(f"No nodes found for {title}. Skipping chart.")
            return

        answered = sum(1 for node in nodes if node.is_answered)
        unanswered = len(nodes) - answered

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["Answered", "Unanswered"],
                    values=[answered, unanswered],
                    marker=dict(colors=["#90EE90", "#FFB6C1"]),
                )
            ]
        )
        fig.update_layout(title=title)

        file_path = export_dir / file_name
        fig.write_html(str(file_path))
        self.logger.info(f"Exported: {file_path}")

    def _generate_timeline_chart(self, export_dir: Path, snapshot: Optional[int] = None) -> None:
        """
        Generate a timeline chart of node creation.

        Args:
            export_dir (Path): Directory to export the chart.
            snapshot (Optional[int]): If provided, only analyze nodes from this snapshot.
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            raise

        if snapshot is not None:
            nodes = [node for node in self.graph.nodes.values() if node.snapshot == snapshot]
            title = f"Questions Created Over Time (Snapshot {snapshot})"
            file_name = f"timeline_snapshot_{snapshot}.html"
        else:
            nodes = list(self.graph.nodes.values())
            title = "Questions Created Over Time"
            file_name = "timeline.html"

        if not nodes:
            self.logger.warning(f"No nodes found for {title}. Skipping chart.")
            return

        # Bin nodes by upload date
        date_counts: Dict[str, int] = {}
        for node in nodes:
            date_str = node.upload_date.strftime("%Y-%m-%d")
            date_counts[date_str] = date_counts.get(date_str, 0) + 1

        dates = sorted(date_counts.keys())
        counts = [date_counts[d] for d in dates]

        fig = go.Figure(
            data=[go.Bar(x=dates, y=counts, marker=dict(color="#87CEEB"))]
        )
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Count",
        )

        file_path = export_dir / file_name
        fig.write_html(str(file_path))
        self.logger.info(f"Exported: {file_path}")

    def _generate_connectivity_chart(self, export_dir: Path, snapshot: Optional[int] = None) -> None:
        """
        Generate a scatter chart of node connectivity (in-degree, out-degree).

        Args:
            export_dir (Path): Directory to export the chart.
            snapshot (Optional[int]): If provided, only analyze nodes from this snapshot.
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            raise

        if snapshot is not None:
            nodes = [node for node in self.graph.nodes.values() if node.snapshot == snapshot]
            title = f"Node Connectivity Analysis (Snapshot {snapshot})"
            file_name = f"connectivity_snapshot_{snapshot}.html"
        else:
            nodes = list(self.graph.nodes.values())
            title = "Node Connectivity Analysis"
            file_name = "connectivity.html"

        if not nodes:
            self.logger.warning(f"No nodes found for {title}. Skipping chart.")
            return

        node_ids = []
        in_degrees = []
        out_degrees = []

        for node in nodes:
            node_id = node.node_id
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
            title=title,
            xaxis_title="Node ID",
            yaxis_title="Degree",
        )

        file_path = export_dir / file_name
        fig.write_html(str(file_path))
        self.logger.info(f"Exported: {file_path}")

    def _generate_dashboard(self, export_dir: Path, snapshots: List[int]) -> None:
        """
        Generate a premium HTML dashboard index that aggregates overall and snapshot-specific statistics.

        Args:
            export_dir (Path): Directory to export the dashboard.
            snapshots (List[int]): List of unique snapshot IDs to include.
        """
        # Build snapshot buttons for the sidebar
        snapshot_buttons = ""
        for s in snapshots:
            snapshot_buttons += f'''
            <button class="nav-btn" onclick="switchTab({s})">
                <span class="icon">📁</span>
                <span>Snapshot {s}</span>
            </button>
            '''

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Learning Progress Tracker - Statistics Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #f1f5f9;
            color: #0f172a;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}
        
        /* Sidebar Styles */
        .sidebar {{
            width: 280px;
            background-color: #0f172a;
            color: #f8fafc;
            display: flex;
            flex-direction: column;
            padding: 24px;
            border-right: 1px solid #1e293b;
        }}
        .brand {{
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 32px;
            background: linear-gradient(to right, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .nav-section-title {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin-bottom: 12px;
            margin-top: 20px;
            font-weight: 700;
        }}
        .nav-btn {{
            background: none;
            border: none;
            color: #94a3b8;
            padding: 12px 16px;
            font-size: 0.95rem;
            font-weight: 500;
            text-align: left;
            cursor: pointer;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: all 0.2s ease;
            width: 100%;
            margin-bottom: 4px;
        }}
        .nav-btn:hover {{
            background-color: #1e293b;
            color: #f8fafc;
        }}
        .nav-btn.active {{
            background-color: #3b82f6;
            color: #ffffff;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
        }}
        .nav-btn .icon {{
            font-size: 1.1rem;
        }}

        /* Main Content Styles */
        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            padding: 40px;
        }}
        .header {{
            margin-bottom: 32px;
        }}
        .header h1 {{
            font-size: 2rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 8px;
        }}
        .header p {{
            color: #64748b;
            font-size: 1rem;
        }}
        
        /* Grid Layout */
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 24px;
            margin-bottom: 24px;
        }}
        @media (max-width: 1100px) {{
            .chart-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* Card Styles */
        .card {{
            background: #ffffff;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            padding: 24px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            display: flex;
            flex-direction: column;
        }}
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
        }}
        .card-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 12px;
        }}
        .chart-container {{
            width: 100%;
            height: 480px;
            position: relative;
            background-color: #fafafa;
            border-radius: 8px;
            overflow: hidden;
        }}
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
            background: transparent;
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="brand">
            <span class="brand-icon">📈</span>
            <span>Learning Tracker</span>
        </div>
        
        <div class="nav-section-title">Analysis</div>
        <button id="btn-overall" class="nav-btn active" onclick="switchTab('overall')">
            <span class="icon">📊</span>
            <span>Overall Progress</span>
        </button>

        <div class="nav-section-title">Snapshots</div>
        <div style="overflow-y: auto; flex: 1; padding-right: 4px;">
            {snapshot_buttons}
        </div>
    </div>

    <div class="main-content">
        <div class="header">
            <h1 id="dashboard-title">Overall Progress Dashboard</h1>
            <p id="dashboard-subtitle">Comprehensive statistics across all nodes and snapshots</p>
        </div>

        <div class="chart-grid">
            <div class="card" style="grid-column: span 1;">
                <div class="card-title">🍰 Answered vs Unanswered</div>
                <div class="chart-container">
                    <iframe id="iframe-answered" src="answered_distribution.html"></iframe>
                </div>
            </div>

            <div class="card" style="grid-column: span 1;">
                <div class="card-title">📅 Node Creation Timeline</div>
                <div class="chart-container">
                    <iframe id="iframe-timeline" src="timeline.html"></iframe>
                </div>
            </div>

            <div class="card" style="grid-column: span 2;">
                <div class="card-title">🔗 Node Connectivity Analysis</div>
                <div class="chart-container">
                    <iframe id="iframe-connectivity" src="connectivity.html"></iframe>
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(mode) {{
            // Remove active class from all buttons
            document.querySelectorAll('.nav-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});

            const answeredIframe = document.getElementById('iframe-answered');
            const timelineIframe = document.getElementById('iframe-timeline');
            const connectivityIframe = document.getElementById('iframe-connectivity');
            const titleEl = document.getElementById('dashboard-title');
            const subtitleEl = document.getElementById('dashboard-subtitle');

            if (mode === 'overall') {{
                document.getElementById('btn-overall').classList.add('active');
                
                answeredIframe.src = 'answered_distribution.html';
                timelineIframe.src = 'timeline.html';
                connectivityIframe.src = 'connectivity.html';
                
                titleEl.textContent = 'Overall Progress Dashboard';
                subtitleEl.textContent = 'Comprehensive statistics across all nodes and snapshots';
            }} else {{
                // Find matching button to activate
                const event = window.event;
                if (event && event.currentTarget) {{
                    event.currentTarget.classList.add('active');
                }} else {{
                    // Fallback to searching buttons
                    const btns = document.querySelectorAll('.nav-btn');
                    for (let btn of btns) {{
                        if (btn.textContent.includes('Snapshot ' + mode)) {{
                            btn.classList.add('active');
                            break;
                        }}
                    }}
                }}

                answeredIframe.src = 'answered_distribution_snapshot_' + mode + '.html';
                timelineIframe.src = 'timeline_snapshot_' + mode + '.html';
                connectivityIframe.src = 'connectivity_snapshot_' + mode + '.html';
                
                titleEl.textContent = 'Snapshot ' + mode + ' Dashboard';
                subtitleEl.textContent = 'Statistics computed exclusively for nodes in snapshot ' + mode;
            }}
        }}
    </script>
</body>
</html>
"""
        dashboard_path = export_dir / "index.html"
        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        self.logger.info(f"Dashboard index exported: {dashboard_path}")
