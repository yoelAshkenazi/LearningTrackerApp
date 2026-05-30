"""
Main Tkinter application window, menu bar, and layout frames.

Orchestrates the overall GUI structure and event handling for the
learning progress tracker.
"""

import copy
import logging
import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path
from datetime import datetime

from .models import LearningGraph, QuestionNode
from .storage import StorageManager
from .gui_canvas import GraphCanvas
from .gui_popups import AddNodePopup, EditNodePopup
from .statistics_engine import StatisticsEngine
from .utils import generate_node_id


class LearningTrackerApp:
    """
    Main application window for the Learning Progress Tracker.

    Manages the menu bar, canvas, and communication between GUI components.

    Attributes:
        root (tk.Tk): The root Tkinter window.
        storage_manager (StorageManager): Handles data persistence.
        graph (LearningGraph): The current learning graph.
        canvas (GraphCanvas): The interactive canvas for drawing the graph.
        current_graph_file (Path): Path to the currently loaded graph file.
        undo_stack (list): History of past graph states for undo.
        redo_stack (list): Reverted states for redo.
    """

    def __init__(self, root: tk.Tk, storage_manager: StorageManager):
        """
        Initialize the main application window.

        Args:
            root (tk.Tk): The root Tkinter window.
            storage_manager (StorageManager): The storage manager instance.
        """
        self.logger = logging.getLogger(__name__)
        self.root = root
        self.storage_manager = storage_manager

        self.undo_stack = []
        self.redo_stack = []

        # Load the graph or create new
        self.graph = self.storage_manager.load_graph()
        if self.graph is None:
            self.graph = LearningGraph(graph_created_at=datetime.now(), snapshot_counter=1)

        self.current_graph_file = self.storage_manager.default_graph_path

        # Keyboard shortcuts
        self.root.bind("<Control-z>", self._undo)
        self.root.bind("<Control-y>", self._redo)

        self._setup_menu_bar()
        self._setup_layout()

    def _setup_menu_bar(self) -> None:
        """Set up the menu bar with File, Edit, and Tools menus."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Graph", command=self._new_graph)
        file_menu.add_command(label="Save", command=self._save_graph)
        file_menu.add_command(label="Load", command=self._load_graph)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self._undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self._redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Selection", command=self._clear_selection)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Generate Statistics", command=self._generate_statistics)

    def _setup_layout(self) -> None:
        """Set up the main layout with frames and canvas."""
        # Control frame (sleek modern light-gray flat toolbar)
        control_frame = tk.Frame(self.root, bg="#EAECEE", height=60)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        instructions = (
            "Left-click to edit node | Shift+Left-click drag to connect/create nodes | "
            "Right-click to add node | Drag to move node"
        )
        tk.Label(
            control_frame, text=instructions, bg="#EAECEE", font=("Arial", 9, "bold"), fg="#566573"
        ).pack(side=tk.LEFT, padx=10, pady=10)

        # Modern flat styling for buttons
        button_style = {
            "bg": "#34495E",
            "fg": "white",
            "activebackground": "#2C3E50",
            "activeforeground": "white",
            "font": ("Arial", 9, "bold"),
            "relief": tk.FLAT,
            "padx": 10,
            "pady": 3,
        }

        self.undo_btn = tk.Button(control_frame, text="Undo", command=self._undo, **button_style)
        self.undo_btn.pack(side=tk.RIGHT, padx=5, pady=10)

        self.redo_btn = tk.Button(control_frame, text="Redo", command=self._redo, **button_style)
        self.redo_btn.pack(side=tk.RIGHT, padx=5, pady=10)

        self._update_undo_redo_buttons()

        # Canvas frame (premium dark border)
        canvas_frame = tk.Frame(self.root, bg="#BDC3C7", bd=1)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.canvas = GraphCanvas(
            canvas_frame,
            self.graph,
            on_node_click=self._on_node_click,
            on_node_moved=self._on_node_moved,
            on_edge_request=self._on_edge_request,
            on_add_node_request=self._on_add_node_request,
            on_connect_create_request=self._on_connect_create_request,
            on_drag_start=self._save_to_undo_stack,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _save_to_undo_stack(self) -> None:
        """Save a deep copy of the current graph to the undo stack."""
        self.undo_stack.append(copy.deepcopy(self.graph))
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self._update_undo_redo_buttons()

    def _undo(self, event=None) -> None:
        """Revert the graph to its previous state."""
        if not self.undo_stack:
            return
        self.redo_stack.append(copy.deepcopy(self.graph))
        if len(self.redo_stack) > 50:
            self.redo_stack.pop(0)
        self.graph = self.undo_stack.pop()
        self.canvas.update_graph(self.graph)
        self._update_undo_redo_buttons()
        self.logger.info("Undo operation executed.")

    def _redo(self, event=None) -> None:
        """Reapply a reverted graph state."""
        if not self.redo_stack:
            return
        self.undo_stack.append(copy.deepcopy(self.graph))
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
        self.graph = self.redo_stack.pop()
        self.canvas.update_graph(self.graph)
        self._update_undo_redo_buttons()
        self.logger.info("Redo operation executed.")

    def _update_undo_redo_buttons(self) -> None:
        """Enable or disable toolbar buttons based on stack state."""
        if hasattr(self, 'undo_btn') and hasattr(self, 'redo_btn'):
            if self.undo_stack:
                self.undo_btn.config(state=tk.NORMAL, bg="#34495E")
            else:
                self.undo_btn.config(state=tk.DISABLED, bg="#BDC3C7")

            if self.redo_stack:
                self.redo_btn.config(state=tk.NORMAL, bg="#34495E")
            else:
                self.redo_btn.config(state=tk.DISABLED, bg="#BDC3C7")

    def _new_graph(self) -> None:
        """Create a new graph with a user-specified name."""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Graph")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog, text="Enter graph name:", font=("Arial", 10)
        ).pack(padx=10, pady=(10, 5), anchor=tk.W)

        name_entry = tk.Entry(dialog, width=40)
        name_entry.pack(padx=10, pady=5)
        name_entry.focus()

        def create():
            graph_name = name_entry.get().strip()
            if not graph_name:
                messagebox.showerror("Error", "Graph name cannot be empty.")
                return

            # Create new graph file
            graph_file = self.storage_manager.data_dir / f"{graph_name}.json"
            self.graph = LearningGraph(graph_created_at=datetime.now(), snapshot_counter=1)
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.current_graph_file = graph_file

            if self.storage_manager.save_graph(self.graph, graph_file):
                self.canvas.update_graph(self.graph)
                self.root.title(f"Learning Progress Tracker - {graph_name}")
                messagebox.showinfo("Success", f"New graph '{graph_name}' created.")
                self.logger.info(f"New graph created: {graph_name}")
                self._update_undo_redo_buttons()
            else:
                messagebox.showerror("Error", "Failed to create graph.")

            dialog.destroy()

        button_frame = tk.Frame(dialog)
        button_frame.pack(padx=10, pady=10)

        tk.Button(button_frame, text="Create", command=create).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def _on_add_node_request(self, x: float, y: float) -> None:
        """
        Handle right-click node addition request.

        Args:
            x (float): Canvas x-coordinate.
            y (float): Canvas y-coordinate.
        """
        node_id = generate_node_id()
        popup = AddNodePopup(
            self.root,
            node_id,
            lambda nid, q, a, diff: self._create_node(nid, q, a, x, y, diff),
        )

    def _on_connect_create_request(self, source_id: str, x: float, y: float) -> None:
        """
        Handle Shift-drag release on empty space for edge connection creation.

        Args:
            source_id (str): Source node identifier.
            x (float): Canvas x-coordinate for new node.
            y (float): Canvas y-coordinate for new node.
        """
        node_id = generate_node_id()
        popup = AddNodePopup(
            self.root,
            node_id,
            lambda nid, q, a, diff: self._create_connected_node(source_id, nid, q, a, x, y, diff),
        )

    def _create_node(
        self,
        node_id: str,
        question: str,
        answer: str = "",
        x: float = 100.0,
        y: float = 100.0,
        difficulty: str = "easy",
    ) -> None:
        """
        Create a new node in the graph.

        Args:
            node_id (str): Unique node identifier.
            question (str): The question text.
            answer (str): The answer text (optional).
            x (float): Canvas x-coordinate.
            y (float): Canvas y-coordinate.
            difficulty (str): The difficulty level.
        """
        self._save_to_undo_stack()
        node = QuestionNode(
            node_id=node_id,
            question=question,
            upload_date=datetime.now(),
            answer=answer,
            is_answered=bool(answer),
            x=x,
            y=y,
            snapshot=self.graph.snapshot_counter,
            difficulty=difficulty,
        )
        self.graph.add_node(node)
        self.canvas.redraw()
        self.logger.info(f"Node created: {node_id}")

    def _create_connected_node(
        self,
        source_id: str,
        node_id: str,
        question: str,
        answer: str = "",
        x: float = 100.0,
        y: float = 100.0,
        difficulty: str = "easy",
    ) -> None:
        """
        Create a new node and add an edge from a source node to it.

        Args:
            source_id (str): Source node ID to connect from.
            node_id (str): Unique identifier for the new node.
            question (str): The question text.
            answer (str): The answer text (optional).
            x (float): Canvas x-coordinate.
            y (float): Canvas y-coordinate.
            difficulty (str): The difficulty level.
        """
        self._save_to_undo_stack()
        node = QuestionNode(
            node_id=node_id,
            question=question,
            upload_date=datetime.now(),
            answer=answer,
            is_answered=bool(answer),
            x=x,
            y=y,
            snapshot=self.graph.snapshot_counter,
            difficulty=difficulty,
        )
        self.graph.add_node(node)
        self.graph.add_edge(source_id, node_id)
        self.canvas.redraw()
        self.logger.info(f"Node created and connected: {source_id} -> {node_id}")

    def _on_node_click(self, node_id: str) -> None:
        """
        Handle node click events.

        Opens the edit dialog for the selected node.

        Args:
            node_id (str): The ID of the clicked node.
        """
        node = self.graph.nodes.get(node_id)
        if node:
            popup = EditNodePopup(
                self.root,
                node,
                on_save=self._update_node,
                on_delete=self._delete_node,
            )

    def _update_node(
        self, node_id: str, question: str, answer: str, is_answered: bool, difficulty: str = "easy"
    ) -> None:
        """
        Update an existing node.

        Args:
            node_id (str): The node to update.
            question (str): Updated question text.
            answer (str): Updated answer text.
            is_answered (bool): Whether the node is answered.
            difficulty (str): The difficulty level.
        """
        self._save_to_undo_stack()
        node = self.graph.nodes.get(node_id)
        if node:
            node.question = question
            node.answer = answer
            node.is_answered = is_answered
            node.difficulty = difficulty
            if is_answered and not node.answer_date:
                node.answer_date = datetime.now()
            self.canvas.redraw()
            self.logger.info(f"Node updated: {node_id}")

    def _delete_node(self, node_id: str) -> None:
        """
        Delete a node from the graph.

        Args:
            node_id (str): The node to delete.
        """
        self._save_to_undo_stack()
        self.graph.remove_node(node_id)
        self.canvas.redraw()
        self.logger.info(f"Node deleted: {node_id}")

    def _on_node_moved(self, node_id: str, x: float, y: float) -> None:
        """
        Handle node drag events.

        Args:
            node_id (str): The moved node.
            x (float): New x-coordinate.
            y (float): New y-coordinate.
        """
        node = self.graph.nodes.get(node_id)
        if node:
            node.x = x
            node.y = y

    def _on_edge_request(self, source_id: str, target_id: str) -> None:
        """
        Handle edge creation requests.

        Args:
            source_id (str): Source node ID.
            target_id (str): Target node ID.
        """
        self._save_to_undo_stack()
        self.graph.add_edge(source_id, target_id)
        self.canvas.redraw()
        self.logger.info(f"Edge created: {source_id} -> {target_id}")

    def _clear_selection(self) -> None:
        """Clear any selected nodes on the canvas."""
        self.canvas.clear_selection()

    def _save_graph(self) -> None:
        """Save the current graph to disk."""
        if self.storage_manager.save_graph(self.graph, self.current_graph_file):
            messagebox.showinfo("Success", "Graph saved successfully.")
            self.logger.info(f"Graph saved: {self.current_graph_file}")
        else:
            messagebox.showerror("Error", "Failed to save graph.")

    def _load_graph(self) -> None:
        """Load a graph from disk."""
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            initialdir=self.storage_manager.data_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if file_path:
            graph = self.storage_manager.load_graph(Path(file_path))
            if graph:
                self.graph = graph
                self.undo_stack.clear()
                self.redo_stack.clear()
                self.current_graph_file = Path(file_path)
                self.canvas.update_graph(self.graph)
                graph_name = Path(file_path).stem
                self.root.title(f"Learning Progress Tracker - {graph_name}")
                messagebox.showinfo("Success", "Graph loaded successfully.")
                self.logger.info(f"Graph loaded: {file_path}")
                self._update_undo_redo_buttons()
            else:
                messagebox.showerror("Error", "Failed to load graph.")

    def _generate_statistics(self) -> None:
        """Generate and export statistics charts."""
        try:
            engine = StatisticsEngine(self.graph, self.storage_manager)
            engine.generate_all_charts()
            messagebox.showinfo("Success", "Statistics exported successfully.")
            self.logger.info("Statistics generated")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate statistics: {e}")
            self.logger.error(f"Statistics generation failed: {e}")
