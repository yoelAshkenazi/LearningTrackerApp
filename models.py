"""
Data models for the Learning Progress Tracker.

Defines the core data structures: QuestionNode and LearningGraph.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict, List


@dataclass
class QuestionNode:
    """
    Represents a single question node in the learning graph.

    Attributes:
        node_id (str): Unique identifier for the node.
        question (str): The question text.
        upload_date (datetime): When the question was created.
        answer_date (Optional[datetime]): When the question was answered.
        answer (str): The answer text (empty if not answered).
        is_answered (bool): Whether the question has been answered.
        x (float): Canvas x-coordinate for visualization.
        y (float): Canvas y-coordinate for visualization.
    """

    node_id: str
    question: str
    upload_date: datetime
    answer_date: Optional[datetime] = None
    answer: str = ""
    is_answered: bool = False
    x: float = 100.0
    y: float = 100.0
    snapshot: int = 1

    def to_dict(self) -> Dict:
        """
        Convert the node to a dictionary for JSON serialization.

        Returns:
            Dict: Dictionary representation with ISO-8601 datetime strings.
        """
        return {
            "question": self.question,
            "upload_date": self.upload_date.isoformat(),
            "answer_date": self.answer_date.isoformat() if self.answer_date else None,
            "answer": self.answer,
            "is_answered": self.is_answered,
            "x": self.x,
            "y": self.y,
            "snapshot": self.snapshot,
        }

    @staticmethod
    def from_dict(node_id: str, data: Dict) -> "QuestionNode":
        """
        Create a QuestionNode from a dictionary (JSON deserialization).

        Args:
            node_id (str): The node's unique identifier.
            data (Dict): Dictionary containing node attributes.

        Returns:
            QuestionNode: Reconstructed node instance.
        """
        return QuestionNode(
            node_id=node_id,
            question=data.get("question", ""),
            upload_date=datetime.fromisoformat(data["upload_date"]),
            answer_date=(
                datetime.fromisoformat(data["answer_date"])
                if data.get("answer_date")
                else None
            ),
            answer=data.get("answer", ""),
            is_answered=data.get("is_answered", False),
            x=data.get("x", 100.0),
            y=data.get("y", 100.0),
            snapshot=data.get("snapshot", 1),
        )


@dataclass
class LearningGraph:
    """
    Represents the entire learning graph structure.

    Attributes:
        graph_created_at (datetime): When the graph was created.
        snapshot_counter (int): Current snapshot count.
        nodes (Dict[str, QuestionNode]): Dictionary of all nodes keyed by node_id.
        edges (List[tuple]): List of directed edges as (source_id, target_id) tuples.
    """

    graph_created_at: datetime
    snapshot_counter: int = 1
    nodes: Dict[str, QuestionNode] = field(default_factory=dict)
    edges: List[tuple] = field(default_factory=list)

    def add_node(self, node: QuestionNode) -> None:
        """
        Add a node to the graph.

        Args:
            node (QuestionNode): The node to add.
        """
        self.nodes[node.node_id] = node

    def remove_node(self, node_id: str) -> None:
        """
        Remove a node and all its connected edges.

        Args:
            node_id (str): The ID of the node to remove.
        """
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.edges = [
                edge for edge in self.edges
                if edge[0] != node_id and edge[1] != node_id
            ]

    def add_edge(self, source_id: str, target_id: str) -> None:
        """
        Add a directed edge between two nodes.

        Args:
            source_id (str): ID of the source node.
            target_id (str): ID of the target node.
        """
        if source_id in self.nodes and target_id in self.nodes:
            if (source_id, target_id) not in self.edges:
                self.edges.append((source_id, target_id))

    def remove_edge(self, source_id: str, target_id: str) -> None:
        """
        Remove a directed edge between two nodes.

        Args:
            source_id (str): ID of the source node.
            target_id (str): ID of the target node.
        """
        self.edges = [
            edge for edge in self.edges
            if not (edge[0] == source_id and edge[1] == target_id)
        ]

    def get_outgoing_edges(self, node_id: str) -> List[str]:
        """
        Get all nodes reachable from a given node.

        Args:
            node_id (str): The source node ID.

        Returns:
            List[str]: List of target node IDs.
        """
        return [target for source, target in self.edges if source == node_id]

    def get_incoming_edges(self, node_id: str) -> List[str]:
        """
        Get all nodes that point to a given node.

        Args:
            node_id (str): The target node ID.

        Returns:
            List[str]: List of source node IDs.
        """
        return [source for source, target in self.edges if target == node_id]

    def to_dict(self) -> Dict:
        """
        Convert the graph to a dictionary for JSON serialization.

        Returns:
            Dict: Dictionary representation with all nodes and edges.
        """
        return {
            "graph_created_at": self.graph_created_at.isoformat(),
            "snapshot_counter": self.snapshot_counter,
            "nodes": {
                node_id: node.to_dict() for node_id, node in self.nodes.items()
            },
            "edges": [
                {"source": source, "target": target} for source, target in self.edges
            ],
        }

    @staticmethod
    def from_dict(data: Dict) -> "LearningGraph":
        """
        Create a LearningGraph from a dictionary (JSON deserialization).

        Args:
            data (Dict): Dictionary containing graph data.

        Returns:
            LearningGraph: Reconstructed graph instance.
        """
        graph = LearningGraph(
            graph_created_at=datetime.fromisoformat(data["graph_created_at"]),
            snapshot_counter=data.get("snapshot_counter", 1),
        )

        for node_id, node_data in data.get("nodes", {}).items():
            graph.add_node(QuestionNode.from_dict(node_id, node_data))

        for edge_data in data.get("edges", []):
            graph.edges.append((edge_data["source"], edge_data["target"]))

        return graph
