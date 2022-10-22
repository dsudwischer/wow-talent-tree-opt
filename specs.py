import json
from enum import Enum

from talent_graph import TalentGraph, TalentNode, NodeConnection


class Spec(str, Enum):
    SHAMAN_ENHANCEMENT = "shaman_enhancement"


def get_talent_graph_by_spec(spec: Spec) -> TalentGraph:
    with open(f"./class_trees/{spec.value}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        nodes = [TalentNode.parse_obj(node) for node in data["nodes"]]
        connections = [NodeConnection.parse_obj(conn) for conn in data["node_connections"]]
        return TalentGraph(nodes, connections)
