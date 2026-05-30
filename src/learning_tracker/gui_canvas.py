"""
Custom Tkinter Canvas for drawing nodes, edges, and handling interactions.

Provides interactive visualization of the learning graph with drag-drop,
click selection, and edge creation capabilities.
"""

import logging
import tkinter as tk
import math
from typing import Callable, Optional

from .models import LearningGraph
from .utils import get_node_color


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
        on_connect_create_request: Callable[[str, float, float], None],
        on_drag_start: Callable[[], None],
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
            on_connect_create_request (Callable): Callback when right-click/Shift-release connection to empty canvas occurs.
            on_drag_start (Callable): Callback triggered when a node drag actually starts.
            **kwargs: Additional tkinter.Frame arguments.
        """
        super().__init__(parent, **kwargs)
        self.logger = logging.getLogger(__name__)

        self.graph = graph
        self.on_node_click = on_node_click
        self.on_node_moved = on_node_moved
        self.on_edge_request = on_edge_request
        self.on_add_node_request = on_add_node_request
        self.on_connect_create_request = on_connect_create_request
        self.on_drag_start = on_drag_start

        self.node_items = {}  # Maps node_id -> canvas_item_id
        self.node_positions = {}  # Maps node_id -> (x, y)
        self.selected_node = None
        self.dragging_node = None
        self.connecting_from_node = None
        self.connection_current_pos = None

        self.drag_start_x = 0
        self.drag_start_y = 0
        self.click_start_x = 0
        self.click_start_y = 0
        self.drag_initiated = False

        # Sleek modern gray canvas background
        self.canvas = tk.Canvas(self, bg="#F8F9FA", cursor="arrow", highlightthickness=0)
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
        Draw a single node based on its difficulty shape.

        Args:
            node_id (str): The node ID.
            x (float): Canvas x-coordinate.
            y (float): Canvas y-coordinate.
        """
        node = self.graph.nodes[node_id]
        color = get_node_color(node, self.graph)

        # Premium green outline cue if the node has been marked as answered
        outline_color = "#2ECC71" if node.is_answered else "black"
        outline_width = 3 if node.is_answered else 2

        radius = 20
        difficulty = getattr(node, "difficulty", "easy").lower()

        if difficulty == "easy":
            item_id = self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=color,
                outline=outline_color,
                width=outline_width,
                tags=node_id,
            )
        elif difficulty == "medium":
            item_id = self.canvas.create_rectangle(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=color,
                outline=outline_color,
                width=outline_width,
                tags=node_id,
            )
        elif difficulty == "hard":
            p1 = (x, y - radius)
            p2 = (x + radius * math.cos(math.radians(30)), y + radius * math.sin(math.radians(30)))
            p3 = (x - radius * math.cos(math.radians(30)), y + radius * math.sin(math.radians(30)))
            item_id = self.canvas.create_polygon(
                p1[0], p1[1],
                p2[0], p2[1],
                p3[0], p3[1],
                fill=color,
                outline=outline_color,
                width=outline_width,
                tags=node_id,
            )
        elif difficulty == "challenging":
            p1 = (x, y - radius)
            p2 = (x + radius, y)
            p3 = (x, y + radius)
            p4 = (x - radius, y)
            item_id = self.canvas.create_polygon(
                p1[0], p1[1],
                p2[0], p2[1],
                p3[0], p3[1],
                p4[0], p4[1],
                fill=color,
                outline=outline_color,
                width=outline_width,
                tags=node_id,
            )
        elif difficulty == "extreme":
            points = []
            r_outer = radius
            r_inner = radius * 0.4
            for i in range(10):
                angle = math.radians(i * 36 - 90)
                r = r_outer if i % 2 == 0 else r_inner
                points.append(x + r * math.cos(angle))
                points.append(y + r * math.sin(angle))
            item_id = self.canvas.create_polygon(
                *points,
                fill=color,
                outline=outline_color,
                width=outline_width,
                tags=node_id,
            )
        else:
            item_id = self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=color,
                outline=outline_color,
                width=outline_width,
                tags=node_id,
            )

        self.node_items[node_id] = item_id
        self.node_positions[node_id] = (x, y)

        # Prefix with a checkmark symbol if answered
        prefix = "✓ " if node.is_answered else ""
        label_text = prefix + node.question[:10] + ("..." if len(node.question) > 10 else "")
        self.canvas.create_text(
            x,
            y,
            text=label_text,
            font=("Arial", 8, "bold" if node.is_answered else "normal"),
            fill="black",
            tags=f"label_{node_id}",
        )

    def _draw_edge(self, source_id: str, target_id: str) -> None:
        """
        Draw a directed edge between two nodes, stopping at their boundaries.

        Args:
            source_id (str): Source node ID.
            target_id (str): Target node ID.
        """
        source_node = self.graph.nodes.get(source_id)
        target_node = self.graph.nodes.get(target_id)

        if source_node and target_node:
            edge_tag = f"edge_{source_id}_{target_id}"
            dx = target_node.x - source_node.x
            dy = target_node.y - source_node.y
            dist = math.hypot(dx, dy)
            if dist > 40:
                ux, uy = dx / dist, dy / dist
                sx, sy = source_node.x + 20 * ux, source_node.y + 20 * uy
                ex, ey = target_node.x - 20 * ux, target_node.y - 20 * uy
            else:
                sx, sy = source_node.x, source_node.y
                ex, ey = target_node.x, target_node.y

            self.canvas.create_line(
                sx,
                sy,
                ex,
                ey,
                arrow=tk.LAST,
                fill="gray",
                width=2,
                tags=(edge_tag, "edge"),
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

    def _update_node_coords(self, node_id: str) -> None:
        """
        Update the canvas coordinates of a node, its label, and connected edges.
        
        Args:
            node_id (str): The ID of the node to update.
        """
        node = self.graph.nodes.get(node_id)
        if not node:
            return

        radius = 20
        item_id = self.node_items.get(node_id)
        if item_id:
            difficulty = getattr(node, "difficulty", "easy").lower()
            if difficulty == "easy":
                self.canvas.coords(
                    item_id,
                    node.x - radius,
                    node.y - radius,
                    node.x + radius,
                    node.y + radius,
                )
            elif difficulty == "medium":
                self.canvas.coords(
                    item_id,
                    node.x - radius,
                    node.y - radius,
                    node.x + radius,
                    node.y + radius,
                )
            elif difficulty == "hard":
                p1 = (node.x, node.y - radius)
                p2 = (node.x + radius * math.cos(math.radians(30)), node.y + radius * math.sin(math.radians(30)))
                p3 = (node.x - radius * math.cos(math.radians(30)), node.y + radius * math.sin(math.radians(30)))
                self.canvas.coords(item_id, p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])
            elif difficulty == "challenging":
                p1 = (node.x, node.y - radius)
                p2 = (node.x + radius, node.y)
                p3 = (node.x, node.y + radius)
                p4 = (node.x - radius, node.y)
                self.canvas.coords(item_id, p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1])
            elif difficulty == "extreme":
                points = []
                r_outer = radius
                r_inner = radius * 0.4
                for i in range(10):
                    angle = math.radians(i * 36 - 90)
                    r = r_outer if i % 2 == 0 else r_inner
                    points.append(node.x + r * math.cos(angle))
                    points.append(node.y + r * math.sin(angle))
                self.canvas.coords(item_id, *points)
            else:
                self.canvas.coords(
                    item_id,
                    node.x - radius,
                    node.y - radius,
                    node.x + radius,
                    node.y + radius,
                )

        # Update text label coordinates
        self.canvas.coords(f"label_{node_id}", node.x, node.y)

        # Update incoming edges
        for source_id in self.graph.get_incoming_edges(node_id):
            source_node = self.graph.nodes.get(source_id)
            if source_node:
                edge_tag = f"edge_{source_id}_{node_id}"
                dx = node.x - source_node.x
                dy = node.y - source_node.y
                dist = math.hypot(dx, dy)
                if dist > 40:
                    ux, uy = dx / dist, dy / dist
                    self.canvas.coords(
                        edge_tag,
                        source_node.x + 20 * ux,
                        source_node.y + 20 * uy,
                        node.x - 20 * ux,
                        node.y - 20 * uy,
                    )
                else:
                    self.canvas.coords(
                        edge_tag,
                        source_node.x,
                        source_node.y,
                        node.x,
                        node.y,
                    )

        # Update outgoing edges
        for target_id in self.graph.get_outgoing_edges(node_id):
            target_node = self.graph.nodes.get(target_id)
            if target_node:
                edge_tag = f"edge_{node_id}_{target_id}"
                dx = target_node.x - node.x
                dy = target_node.y - node.y
                dist = math.hypot(dx, dy)
                if dist > 40:
                    ux, uy = dx / dist, dy / dist
                    self.canvas.coords(
                        edge_tag,
                        node.x + 20 * ux,
                        node.y + 20 * uy,
                        target_node.x - 20 * ux,
                        target_node.y - 20 * uy,
                    )
                else:
                    self.canvas.coords(
                        edge_tag,
                        node.x,
                        node.y,
                        target_node.x,
                        target_node.y,
                    )

    def _on_canvas_click(self, event) -> None:
        """
        Handle canvas left-click events.

        Args:
            event: Tkinter event object.
        """
        node_id = self._get_node_at_position(event.x, event.y)

        self.click_start_x = event.x
        self.click_start_y = event.y
        self.drag_initiated = False

        if node_id:
            # Shift key check: state & 0x0001 (Shift pressed)
            if event.state & 0x0001:
                self.connecting_from_node = node_id
                self.connection_current_pos = (event.x, event.y)
            else:
                self.selected_node = node_id
                self.dragging_node = node_id
                self.drag_start_x = event.x
                self.drag_start_y = event.y
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
        Handle canvas drag events for moving nodes or drawing connections.

        Args:
            event: Tkinter event object.
        """
        if self.dragging_node:
            node = self.graph.nodes.get(self.dragging_node)
            if not node:
                return

            if not self.drag_initiated:
                self.drag_initiated = True
                self.on_drag_start()

            # Calculate delta from start position
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y

            # Update node position
            node.x += dx
            node.y += dy

            # Update drag start for next iteration
            self.drag_start_x = event.x
            self.drag_start_y = event.y

            # Update canvas coordinates dynamically (extremely fast, no trails!)
            self._update_node_coords(self.dragging_node)

        elif self.connecting_from_node:
            self.connection_current_pos = (event.x, event.y)
            source_node = self.graph.nodes.get(self.connecting_from_node)
            if source_node:
                self.canvas.delete("temp_edge")
                dx = event.x - source_node.x
                dy = event.y - source_node.y
                dist = math.hypot(dx, dy)
                if dist > 20:
                    ux, uy = dx / dist, dy / dist
                    sx, sy = source_node.x + 20 * ux, source_node.y + 20 * uy
                else:
                    sx, sy = source_node.x, source_node.y
                self.canvas.create_line(
                    sx,
                    sy,
                    event.x,
                    event.y,
                    arrow=tk.LAST,
                    fill="red",
                    width=2,
                    dash=(4, 4),
                    tags="temp_edge",
                )

    def _on_canvas_release(self, event) -> None:
        """
        Handle canvas release events.

        Args:
            event: Tkinter event object.
        """
        # Determine if it was a quick click rather than a drag
        dx = abs(event.x - self.click_start_x)
        dy = abs(event.y - self.click_start_y)
        is_click = (dx < 5 and dy < 5)

        if self.dragging_node:
            node = self.graph.nodes.get(self.dragging_node)
            if node:
                if is_click:
                    # Open the node info popup ONLY on actual click
                    self.on_node_click(self.dragging_node)
                else:
                    self.on_node_moved(self.dragging_node, node.x, node.y)
            self.dragging_node = None
            self.redraw()

        elif self.connecting_from_node:
            target_node_id = self._get_node_at_position(event.x, event.y)
            if target_node_id:
                if target_node_id != self.connecting_from_node:
                    self.on_edge_request(self.connecting_from_node, target_node_id)
            else:
                # Released on empty space -> Trigger Connect & Create new node!
                self.on_connect_create_request(self.connecting_from_node, event.x, event.y)
            
            # Clean up temporary edge rendering
            self.canvas.delete("temp_edge")
            self.connecting_from_node = None
            self.connection_current_pos = None
            self.redraw()

    def clear_selection(self) -> None:
        """Clear the currently selected node."""
        self.selected_node = None
