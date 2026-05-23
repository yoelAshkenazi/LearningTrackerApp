"""
Toplevel Tkinter windows for adding/editing node details and displaying
node information.

Provides dialog boxes for user interaction with individual nodes.
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from models import QuestionNode


class AddNodePopup:
    """
    Dialog for creating a new learning node.

    Attributes:
        root (tk.Tk): Parent window.
        node_id (str): The new node's ID.
        on_create (Callable): Callback when node is created.
    """

    def __init__(self, root: tk.Tk, node_id: str, on_create: Callable):
        """
        Initialize the AddNodePopup.

        Args:
            root (tk.Tk): Parent window.
            node_id (str): The new node's ID.
            on_create (Callable): Callback function (node_id, question, answer).
        """
        self.logger = logging.getLogger(__name__)
        self.node_id = node_id
        self.on_create = on_create

        self.popup = tk.Toplevel(root)
        self.popup.title("Add New Node")
        self.popup.geometry("500x300")

        self._setup_widgets()

    def _setup_widgets(self) -> None:
        """Set up the dialog widgets."""
        # Question
        tk.Label(self.popup, text="Question:").pack(padx=10, pady=(10, 0), anchor=tk.W)
        self.question_text = tk.Text(self.popup, height=5, width=50)
        self.question_text.pack(padx=10, pady=5)

        # Answer
        tk.Label(self.popup, text="Answer (optional):").pack(padx=10, pady=(10, 0), anchor=tk.W)
        self.answer_text = tk.Text(self.popup, height=5, width=50)
        self.answer_text.pack(padx=10, pady=5)

        # Buttons
        button_frame = tk.Frame(self.popup)
        button_frame.pack(padx=10, pady=10, fill=tk.X)

        tk.Button(button_frame, text="Create", command=self._create).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.popup.destroy).pack(side=tk.LEFT, padx=5)

    def _create(self) -> None:
        """Create the node and close the dialog."""
        question = self.question_text.get("1.0", tk.END).strip()
        answer = self.answer_text.get("1.0", tk.END).strip()

        if not question:
            tk.messagebox.showerror("Error", "Question cannot be empty.")
            return

        self.on_create(self.node_id, question, answer)
        self.popup.destroy()


class EditNodePopup:
    """
    Dialog for editing an existing learning node.

    Attributes:
        root (tk.Tk): Parent window.
        node (QuestionNode): The node being edited.
        on_save (Callable): Callback when node is saved.
        on_delete (Callable): Callback when node is deleted.
    """

    def __init__(
        self,
        root: tk.Tk,
        node: QuestionNode,
        on_save: Callable,
        on_delete: Callable,
    ):
        """
        Initialize the EditNodePopup.

        Args:
            root (tk.Tk): Parent window.
            node (QuestionNode): The node to edit.
            on_save (Callable): Callback (node_id, question, answer, is_answered).
            on_delete (Callable): Callback (node_id).
        """
        self.logger = logging.getLogger(__name__)
        self.node = node
        self.on_save = on_save
        self.on_delete = on_delete

        self.popup = tk.Toplevel(root)
        self.popup.title(f"Edit Node: {node.node_id}")
        self.popup.geometry("600x500")

        self._setup_widgets()

    def _setup_widgets(self) -> None:
        """Set up the dialog widgets."""
        # Node ID (read-only)
        tk.Label(self.popup, text=f"Node ID: {self.node.node_id}", font=("Arial", 10, "bold")).pack(
            padx=10, pady=(10, 5), anchor=tk.W
        )

        # Upload date
        tk.Label(self.popup, text=f"Upload Date: {self.node.upload_date.isoformat()}").pack(
            padx=10, pady=(5, 5), anchor=tk.W
        )

        # Answer date
        answer_date_str = (
            self.node.answer_date.isoformat() if self.node.answer_date else "Not answered"
        )
        tk.Label(self.popup, text=f"Answer Date: {answer_date_str}").pack(
            padx=10, pady=(5, 10), anchor=tk.W
        )

        # Question
        tk.Label(self.popup, text="Question:").pack(padx=10, pady=(10, 0), anchor=tk.W)
        self.question_text = tk.Text(self.popup, height=4, width=60)
        self.question_text.pack(padx=10, pady=5)
        self.question_text.insert("1.0", self.node.question)

        # Answer
        tk.Label(self.popup, text="Answer:").pack(padx=10, pady=(10, 0), anchor=tk.W)
        self.answer_text = tk.Text(self.popup, height=4, width=60)
        self.answer_text.pack(padx=10, pady=5)
        self.answer_text.insert("1.0", self.node.answer)

        # Is Answered checkbox
        self.is_answered_var = tk.BooleanVar(value=self.node.is_answered)
        tk.Checkbutton(self.popup, text="Mark as Answered", variable=self.is_answered_var).pack(
            padx=10, pady=5, anchor=tk.W
        )

        # Buttons
        button_frame = tk.Frame(self.popup)
        button_frame.pack(padx=10, pady=10, fill=tk.X)

        tk.Button(button_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", command=self._delete, fg="red").pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(button_frame, text="Cancel", command=self.popup.destroy).pack(side=tk.LEFT, padx=5)

    def _save(self) -> None:
        """Save the node and close the dialog."""
        question = self.question_text.get("1.0", tk.END).strip()
        answer = self.answer_text.get("1.0", tk.END).strip()
        is_answered = self.is_answered_var.get()

        if not question:
            tk.messagebox.showerror("Error", "Question cannot be empty.")
            return

        self.on_save(self.node.node_id, question, answer, is_answered)
        self.popup.destroy()

    def _delete(self) -> None:
        """Delete the node and close the dialog."""
        import tkinter.messagebox as messagebox

        if messagebox.askyesno("Confirm Delete", "Delete this node?"):
            self.on_delete(self.node.node_id)
            self.popup.destroy()
