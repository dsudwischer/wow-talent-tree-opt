from collections import defaultdict
from typing import List, Dict

from pydantic import BaseModel, conint


class Talent(BaseModel):
    name: str
    id: int


class TalentNode(BaseModel):
    node_id: int
    talent_choices: List[Talent]
    max_points: int
    minimum_points_spent: int
    row: conint(ge=0)
    col: conint(ge=0)


class NodeConnection(BaseModel):
    parent_node_id: int
    child_node_id: int


class TalentGraph:
    def __init__(self, nodes: List[TalentNode], connections: List[NodeConnection]):
        self._nodes: List[TalentNode] = nodes
        self._connections: List[NodeConnection] = connections
        self._node_id_to_node: Dict[int, TalentNode] = {}
        self._parent_node_id_to_child_ids: Dict[int, List[int]] = defaultdict(list)
        for node in self._nodes:
            self._node_id_to_node[node.node_id] = node
        for conn in self._connections:
            self._parent_node_id_to_child_ids[conn.parent_node_id].append(conn.child_node_id)
