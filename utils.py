"""
Helper functions for timestamp binning, color generation, and subgraph
traversal.

Provides utility functions used across the application.
"""

import uuid
from datetime import datetime
from typing import Set

from models import QuestionNode, LearningGraph


def generate_node_id() -> str:
    """
    Generate a unique node ID.

    Returns:
        str: A unique identifier (UUID4).
    """
    return str(uuid.uuid4())


def get_node_color(node: QuestionNode, graph: LearningGraph) -> str:
    """
    Dynamically calculate node color based on its snapshot relative to the graph's snapshot range.

    Divides the snapshot range [1, graph.snapshot_counter] into 5 equal bins and assigns colors:
    - Bin 0: #FFB3BA (light red)
    - Bin 1: #FFCCCB (light pink)
    - Bin 2: #FFFFBA (light yellow)
    - Bin 3: #BAE1BA (light green)
    - Bin 4: #BAC2FF (light blue)

    Args:
        node (QuestionNode): The node to color.
        graph (LearningGraph): The graph for snapshot context.

    Returns:
        str: A hex color code.
    """
    colors = ["#FFB3BA", "#FFCCCB", "#FFFFBA", "#BAE1BA", "#BAC2FF"]

    s_min = 1
    s_max = graph.snapshot_counter

    if s_max <= s_min:
        return colors[0]

    # Normalize snapshot to [0, 1] range
    val = (node.snapshot - s_min) / (s_max - s_min)
    bin_index = min(4, int(val * 5))

    return colors[max(0, bin_index)]


def get_subgraph(graph: LearningGraph, start_node_id: str, direction: str = "forward") -> Set[str]:
    """
    Get all nodes reachable from a start node (forward or backward traversal).

    Args:
        graph (LearningGraph): The graph to traverse.
        start_node_id (str): The starting node ID.
        direction (str): "forward" for outgoing edges, "backward" for incoming edges.

    Returns:
        Set[str]: Set of reachable node IDs.
    """
    visited = set()
    stack = [start_node_id]

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)

        if direction == "forward":
            neighbors = graph.get_outgoing_edges(current)
        else:
            neighbors = graph.get_incoming_edges(current)

        for neighbor in neighbors:
            if neighbor not in visited:
                stack.append(neighbor)

    return visited


def bin_timestamps(timestamps: list, num_bins: int = 5) -> dict:
    """
    Bin a list of timestamps into equal intervals.

    Args:
        timestamps (list): List of datetime objects.
        num_bins (int): Number of bins to create.

    Returns:
        dict: Dictionary mapping bin index to list of timestamps in that bin.
    """
    if not timestamps:
        return {i: [] for i in range(num_bins)}

    t_min = min(timestamps)
    t_max = max(timestamps)
    total_span = (t_max - t_min).total_seconds()

    bins = {i: [] for i in range(num_bins)}

    for ts in timestamps:
        if total_span == 0:
            bin_index = 0
        else:
            bin_index = min(num_bins - 1, int(((ts - t_min).total_seconds() / total_span) * num_bins))
        bins[bin_index].append(ts)

    return bins
