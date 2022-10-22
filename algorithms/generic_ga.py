import itertools
import random
from typing import List, TypeVar, Callable, Generic, Optional

T = TypeVar("T")


class Individual(Generic[T]):
    def __init__(self, genome: T, score_function: Callable[[T], float]) -> None:
        self._genome: T = genome
        self._score_function: Callable[[T], float] = score_function

    def score(self) -> float:
        return self._score_function(self._genome)

    def mutate(self, mutation_function: Callable[[T], T]) -> "Individual[T]":
        self._genome = mutation_function(self._genome)
        return self

    def get_genome(self) -> T:
        return self._genome


def _maybe_mutate(
        individual: Individual[T],
        mutation_function: Callable[[T], T],
        mutation_probability: float,
) -> Individual[T]:
    if random.random() < mutation_probability:
        individual.mutate(mutation_function)
    return individual


class Population(Generic[T]):
    def __init__(self,
                 individuals: Optional[List[Individual[T]]],
                 crossover_function: Callable[[Individual[T], Individual[T]], Individual[T]],
                 mutation_function: Callable[[Individual[T]], Individual[T]],
                 elitism_rate: float = 0.5,
                 mutation_probability: float = 0.1,
                 ) -> None:
        if len(individuals) < 2:
            raise ValueError("Population must have at least 2 individuals")
        self._individuals: List[Individual[T]] = individuals
        self._target_population_size: int = len(self._individuals)
        self._crossover_function: Callable[[Individual[T], Individual[T]], Individual[T]] = crossover_function
        self._keep_top_n = int(self._target_population_size * elitism_rate)
        self._num_offsprings = self._target_population_size - self._keep_top_n
        self._mutation_function: Callable[[Individual[T]], Individual[T]] = mutation_function
        self._mutation_probability = mutation_probability

    def get_individuals(self) -> List[Individual[T]]:
        return self._individuals

    def _do_one_generation(self) -> None:
        self._individuals.sort(key=lambda individual: individual.score(), reverse=True)
        kept_population_part: List[Individual[T]] = self._individuals[:self._keep_top_n]
        offspring_part: List[Individual[T]] = list(itertools.chain(*[
            [self._crossover_function(i1, i2) for i1, i2 in random.sample(kept_population_part, 2)]
            for _ in range(self._num_offsprings)
        ]))
        mutated_offspring_part: List[Individual[T]] = [
            _maybe_mutate(individual, self._mutation_function, self._mutation_probability) for individual in
            offspring_part]
        self._individuals = kept_population_part + mutated_offspring_part

    def evolve(self, num_generations: int) -> None:
        for _ in range(num_generations):
            self._do_one_generation()
