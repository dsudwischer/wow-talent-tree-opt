from algorithms.generic_ga import Population, Individual
from specs import Spec, get_talent_graph_by_spec
from talent_graph import TalentBuild, TalentGraph, grow_random_tree
from cachetools import cached, LFUCache


_POPULATION_SIZE = 100


def _cache_key(talent_build: TalentBuild) -> str:
    return str(talent_build)


@cached(cache=LFUCache(maxsize=1_000_000_000), key=_cache_key)
def dps_score(talent_build: TalentBuild) -> float:
    raise NotImplementedError()  # ToDo: Run simc here to find out DPS


def crossover_function(i1: Individual[TalentBuild], i2: Individual[TalentBuild]) -> Individual[TalentBuild]:
    raise NotImplementedError()  # ToDo: Implement a suitable crossover function


def mutate(individual: Individual[TalentBuild]) -> Individual[TalentBuild]:
    raise NotImplementedError()  # ToDo: Implement a suitable mutation function


def make_individual(talent_graph: TalentGraph, max_points: int) -> Individual[TalentBuild]:
    return Individual(grow_random_tree(talent_graph, max_points, [], []), dps_score)


def make_population(talent_graph: TalentGraph, max_points: int, size: int) -> Population[TalentBuild]:
    return Population(
        individuals=[make_individual(talent_graph, max_points) for _ in range(size)],
        crossover_function=crossover_function,
        mutation_function=mutate,
        elitism_rate=0.5,
        mutation_probability=0.1
    )


def run(spec: Spec, num_talent_points: int, num_generations: int) -> Population[TalentBuild]:
    talent_graph = get_talent_graph_by_spec(spec)
    population = make_population(talent_graph, num_talent_points, _POPULATION_SIZE)
    population.evolve(num_generations)
    return population
