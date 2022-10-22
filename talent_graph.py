import dataclasses
import random
from collections import defaultdict
from enum import Enum
from typing import List, Dict, Container, Set

from pydantic import BaseModel, conint

from util import lists_are_equal, unique_elements


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

    def __hash__(self) -> int:
        return hash(self.node_id)


class NodeConnection(BaseModel):
    parent_node_id: int
    child_node_id: int


class TalentGraph:
    def __init__(self, nodes: List[TalentNode], connections: List[NodeConnection]):
        self._nodes: List[TalentNode] = nodes
        self._connections: List[NodeConnection] = connections
        self._node_id_to_node: Dict[int, TalentNode] = {}
        self._parent_node_id_to_child_ids: Dict[int, List[int]] = defaultdict(list)
        self._root_nodes: List[TalentNode] = []
        self._talent_name_by_talent_id: Dict[int, str] = {}
        for node in self._nodes:
            self._node_id_to_node[node.node_id] = node
            for talent in node.talent_choices:
                self._talent_name_by_talent_id[talent.id] = talent.name
        for conn in self._connections:
            self._parent_node_id_to_child_ids[conn.parent_node_id].append(conn.child_node_id)
        nodes_without_parents: Set[int] = set(self._node_id_to_node.keys())
        for conn in self._connections:
            if conn.child_node_id in nodes_without_parents:
                nodes_without_parents.remove(conn.child_node_id)
        self._root_nodes.extend(self._node_id_to_node[node_id] for node_id in nodes_without_parents)

    def get_node_by_id(self, node_id: int) -> TalentNode:
        return self._node_id_to_node[node_id]

    def get_child_nodes(self, node_id: int) -> List[TalentNode]:
        return [self.get_node_by_id(child_id) for child_id in self._parent_node_id_to_child_ids[node_id]]

    def get_root_nodes(self, maximum_points_required: int) -> List[TalentNode]:
        return [node for node in self._root_nodes if node.minimum_points_spent <= maximum_points_required]

    def get_talent_name_by_id(self, talent_id: int) -> str:
        return self._talent_name_by_talent_id[talent_id]


@dataclasses.dataclass(eq=True)
class TalentChoice:
    node_id: int
    talent_id: int
    points: int = 1

    def __str__(self) -> str:
        return f"{self.talent_id}:{self.points}"


class TalentBuild:
    def __init__(self, choices: List[TalentChoice]):
        self._choices: List[TalentChoice] = choices

    def __eq__(self, other):
        if isinstance(other, TalentBuild):
            return lists_are_equal(self._choices, other._choices)
        return False

    def __str__(self) -> str:
        return "/".join(str(choice) for choice in sorted(self._choices, key=lambda choice: choice.node_id))

    def to_readable_string(self, talent_graph: TalentGraph) -> str:
        return "/".join(f"{talent_graph.get_talent_name_by_id(choice.talent_id)}:{choice.points}" for choice in
                        sorted(self._choices, key=lambda choice: choice.node_id))


def _get_valid_next_node_choices(talent_graph: TalentGraph, choice_id_to_current_choice: Dict[int, TalentChoice]) -> \
        List[TalentNode]:
    spent_points = sum(choice.points for choice in choice_id_to_current_choice.values())
    # Root nodes are always valid choices unless they are already taken
    valid_nodes: List[TalentNode] = [node for node in talent_graph.get_root_nodes(spent_points) if
                                     node.node_id not in choice_id_to_current_choice or node.max_points <
                                     choice_id_to_current_choice[node.node_id].points]
    for choice in choice_id_to_current_choice.values():
        node = talent_graph.get_node_by_id(choice.node_id)
        # If we have not fully talented into this node, we cannot move on to child nodes
        if choice.points < node.max_points and spent_points >= node.minimum_points_spent:
            valid_nodes.append(node)
        else:
            for child in talent_graph.get_child_nodes(choice.node_id):
                points_spent_on_child = choice_id_to_current_choice[
                    child.node_id].points if child.node_id in choice_id_to_current_choice else 0
                if child.max_points > points_spent_on_child and spent_points >= child.minimum_points_spent:
                    valid_nodes.append(child)
    return unique_elements(valid_nodes)


def _get_valid_next_talent_choices(valid_nodes: List[TalentNode], ignore_talent_ids: Container[int],
                                   choices_by_id: Dict[int, TalentChoice]) -> List[TalentChoice]:
    valid_choices: List[TalentChoice] = []
    for node in valid_nodes:
        for talent in node.talent_choices:
            if talent.id not in ignore_talent_ids:
                # If we have already chosen the same talent, increment the points by 1. Else set it to 1.
                points = 1 if node.node_id not in choices_by_id else choices_by_id[node.node_id].points + 1
                valid_choices.append(TalentChoice(node.node_id, talent.id, points))
    return valid_choices


class TalentSelectionStrategy(str, Enum):
    UNIFORM = "uniform"
    DEPTH_PROPORTIONAL = "depth_proportional"


def _choose_talent(talent_graph: TalentGraph, valid_choices: List[TalentChoice],
                   strategy: TalentSelectionStrategy) -> TalentChoice:
    if len(valid_choices) == 0:
        raise ValueError("No valid choices to choose from")
    if strategy == TalentSelectionStrategy.UNIFORM:
        return random.choice(valid_choices)
    elif strategy == TalentSelectionStrategy.DEPTH_PROPORTIONAL:
        weights = [talent_graph.get_node_by_id(choice.node_id).row for choice in valid_choices]
        return random.choices(valid_choices, weights=weights, k=1)[0]
    else:
        raise ValueError(f"Unknown talent selection strategy: {strategy}.")


def grow_random_tree(talent_graph: TalentGraph, max_points: int, initial_choices: List[TalentChoice],
                     ignore_talent_ids: Container[int],
                     talent_selection_strategy: TalentSelectionStrategy) -> TalentBuild:
    choices_by_id: Dict[int, TalentChoice] = {choice.node_id: choice for choice in initial_choices}
    spent_points = sum(choice.points for choice in choices_by_id.values())
    if spent_points > max_points:
        raise ValueError("Initial choices exceed max points")
    while spent_points < max_points:
        valid_nodes = _get_valid_next_node_choices(talent_graph, choices_by_id)
        valid_choices = _get_valid_next_talent_choices(valid_nodes, ignore_talent_ids, choices_by_id)
        if not valid_choices:
            break
        choice = _choose_talent(talent_graph, valid_choices, talent_selection_strategy)
        choices_by_id[choice.node_id] = choice
        spent_points += 1
    return TalentBuild(choices=list(choices_by_id.values()))
