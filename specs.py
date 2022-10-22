import json
from enum import Enum

from talent_graph import TalentGraph


class Spec(Enum, str):
    SHAMAN_ENHANCEMENT = "shaman_enhancement"


def get_talent_graph_by_spec(spec: Spec) -> TalentGraph:
    with open(f"./class_trees/{spec.value}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return TalentGraph.parse_obj(data)
