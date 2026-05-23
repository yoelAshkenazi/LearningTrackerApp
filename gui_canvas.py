"""
Custom Tkinter Canvas for drawing nodes, edges, and handling interactions.

Provides interactive visualization of the learning graph with drag-drop,
click selection, and edge creation capabilities.
"""

import logging
import tkinter as tk
from typing import Callable, Optional

from models import LearningGraph
from utils import get_node_color


class GraphCanvas(tk.Frame):
    """
    Custom canvas widget for visualizing and interacting with the learning graph.

    Attributes:
        canvas (tk.Canvas): The underlying Tkinter canvas.
        graph (LearningGraph): The learning graph to display.
        node_items (dict): Maps node IDs to canvas item IDs.
        selected_node (Optional[str]): Currently selected node ID.
        dragging_node (Optional[str]): Currently dragged node ID.
    """

    def __init__(
        self,
        parent,
        graph: LearningGraph,
        on_node_click: Callable[[str], None],
        on_node_moved: Callable[[str, float, float], None],
        on_edge_request: Callable[[str, str], None],
        on_add_node_request: Callable[[float, float], None],
        **kwargs
    ):
        """
        Initialize the GraphCanvas.

        Args:
            parent: Parent Tkinter widget.
            graph (LearningGraph): The learning graph.
            on_node_click (Callable): Callback when a node is clicked.
            on_node_moved (Callable): Callback when a node is moved.
            on_edge_request (Callable): Callback when edge creation is requested.
            on_add_node_request (Callable): Callback for right-click node addition.
            **kwargs: Additional tkinter.Frame arguments.
        """
        super().__init__(parent, **kwargs)
        self.logger = logging.getLogger(__name__)

        self.graph = graph
        self.on_node_click = on_node_click
        self.on_node_moved = on_node_moved
        self.on_edge_request = on_edge_request
        self.on_add_node_request = on_add_node_request

        self.node_items = {}  # Maps node_id -> canvas_item_id
        self.node_positions = {}  # Maps node_id -> (x, y)
        self.selected_node = None
        self.dragging_node = None
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.canvas = tk.Canvas(self, bg="white", cursor="arrow")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind events
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Button-3>", self._on_canvas_right_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)

        self.redraw()

    def update_graph(self, graph: LearningGraph) -> None:
        """
        Update the displayed graph.

        Args:
            graph (LearningGraph): The new graph to display.
        """
        self.graph = graph
        self.redraw()

    def redraw(self) -> None:
        """Redraw all nodes and edges on the canvas."""
        self.canvas.delete("all")
        self.node_items.clear()
        self.node_positions.clear()

        # Draw edges first (so they appear behind nodes)
        for source_id, target_id in self.graph.edges:
            self._draw_edge(source_id, target_id)

        # Draw nodes
        for node_id, node in self.graph.nodes.items():
            self._draw_node(node_id, node.x, node.y)

    def _draw_node(self, node_id: str, x: float, y: float) -> None:
        """
        Draw a single node as a rounded circle.

        Args:
            node_id (str): The node ID.
            x (float): Canvas x-coordinate.
            y (float): Canvas y-coordinate.
        """
        node = self.graph.nodes[node_id]
        color = get_node_color(node, self.graph)

        radius = 20
        item_id = self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=color,
            outline="black",
            width=2,
            tags=node_id,
        )

        self.node_items[node_id] = item_id
        self.node_positions[node_id] = (x, y)

        # Add text label
        label_text = node.question[:10] + ("..." if len(node.question) > 10 else "")
        self.canvas.create_text(
            x,
            y,
            text=label_text,
            font=("Arial", 8),
            fill="black",
            tags=f"label_{node_id}",
        )

    def _draw_edge(self, source_id: str, target_id: str) -> None:
        """
        Draw a directed edge between two nodes.

        Args:
            source_id (str): Source node ID.
            target_id (str): Target node ID.
        """
        source_node = self.graph.nodes.get(source_id)
        target_node = self.graph.nodes.get(target_id)

        if source_node and target_node:
            self.canvas.create_line(
                source_node.x,
                source_node.y,
                target_node.x,
                target_node.y,
                arrow=tk.LAST,
                fill="gray",
                width=2,
            )

    def _get_node_at_position(self, x: int, y: int) -> Optional[str]:
        """
        Get the node ID at a specific canvas position.

        Args:
            x (int): Canvas x-coordinate.
            y (int): Canvas y-coordinate.

        Returns:
            Optional[str]: Node ID if found, None otherwise.
        """
        clicked_items = self.canvas.find_overlapping(
            x - 5, y - 5, x + 5, y + 5
        )

        for item_id in clicked_items:
            tags = self.canvas.gettags(item_id)
            if tags:
                tag = tags[0]
                if tag in self.graph.nodes:
                    return tag
        return None

    def _on_canvas_click(self, event) -> None:
        """
        Handle canvas left-click events.

        Args:
            event: Tkinter event object.
        """
        node_id = self._get_node_at_position(event.x, event.y)

        if node_id:
            self.selected_node = node_id
            self.dragging_node = node_id
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.on_node_click(node_id)
        else:
            self.clear_selection()

    def _on_canvas_right_click(self, event) -> None:
        """
        Handle canvas right-click events for adding nodes.

        Args:
            event: Tkinter event object.
        """
        self.on_add_node_request(event.x, event.y)

    def _on_canvas_drag(self, event) -> None:
        """
        Handle canvas drag events for moving nodes.

        Args:
            event: Tkinter event object.
        """
        if not self.dragging_node:
            return

        node = self.graph.nodes.get(self.dragging_node)
        if not node:
            return

        # Calculate delta from start position
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        # Update node position
        node.x += dx
        node.y += dy

        # Update drag start for next iteration
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        # Redraw immediately
        self.redraw()

    def _on_canvas_release(self, event) -> None:
        """
        Handle canvas release events.

        Args:
            event: Tkinter event object.
        """
        if self.dragging_node:
            node = self.graph.nodes.get(self.dragging_node)
            if node:
                self.on_node_moved(self.dragging_node, node.x, node.y)
            self.dragging_node = None

    def clear_selection(self) -> None:
        """Clear the currently selected node."""
        self.selected_node = None
