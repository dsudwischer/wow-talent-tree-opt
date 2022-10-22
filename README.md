# World of Warcraft Talent Tree Optimization

## Into

In World of Warcraft: Dragonflight, talent trees are revamped and feature a large number of n odes to choose from.
Paired with the fact that, at max level, players can spend a total of 30 points in their specialization tree alone, the
number of combinations reaches multiple millions[^1]. This makes a brute force search for the optimal talent selection
infeasible. Overcoming this hurdle requires an approach that is able to find approximately optimal solutions to this
decision problem in a reasonable amount of time.

## Approach

This repository contains Python implementation of algorithms to find good talent tree setups with a configurable amount
of computational resources. It relies on SimulationCraft[^2] to simulate the performance of different talent trees.

[^1]: https://support.raidbots.com/article/42-talent-tree-combination-size

[^2]: https://simulationcraft.org/
