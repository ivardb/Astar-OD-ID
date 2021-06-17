This code base was used to research extending A*-ID-OD with matching.
The paper for this can be found here: TODO

# MAPFM with A*-ID-OD
A*-ID-OD for matching is an extension of A*-ID-OD made to solve Multi-Agent Pathfinding problems with matching.
This implementation was made for the purpose of comparing it to other algorithms that try and solve the same problem,
namely EPEA*, M*, CBM and ICTS.

## MAPFM
MAPFM is a problem where multiple agents have to go from their start location to a goal that belongs to the same color or team as they do.
The agents are not allowed to swap places or be in the same spot at the same time.
The goal is to optimize the Sum of Individual Costs.
As a final note, agents stay at their goal until all agents have arrived. This means they can still cause collisions there.

## A*+ID+OD
A more in-depth explanation can be found in "Finding optimal solutions to cooperative pathfinding problems" (Standley 2010)
### A*
A* is a heuristic based pathfinder.
It expands states based on a heuristic estimation as well as its current cost.
With a good heuristic this algorithm is fast, optimal and complete.

### OD
OD or operator decomposition changes the way A* expands states.
Instead of all agents moving at the same time, only one agent moves at a time. This reduces the branching factor greatly.

### ID
ID or independence detection tries to solve agents individually first.
It then tries to resolve conflicts by prioritizing one group over another.
If this does not work it will merge the groups and continue until no conflicts remain.

## Matching options
A few matching options have been implemented
- Heuristic Matching
- Exhaustive Matching
- Exhaustive Matching with ID
- Exhaustive Matching with ID and Sorting

All options are both complete and optimal.
Of these heuristic matching performs by far the worst.
ID improves performance on more open maps with multiple teams and sorting improves performance on all maps.

### Heuristic Matching
For this we simply change the A* heuristic to send an agent to the nearest goal of the same color/team
If this sends multiple agents to the same goal it performs bad.

### Exhaustive Matching
For this we create all matchings and then prune by calculating the maximum cost a group of agents can have, given that the solution needs to be better than the best found solution so far.

### Exhaustive Matching with ID
For this we observe that teams have independent matchings if their best matching causes no conflicts with any other group.
This allows us to generate a lot fewer matchings.

### Exhaustive Matching with ID and Sorting
Sorting is an idea proposed by Jaap de Jong where we use a priority queue to sort the matches based on their initial heuristic.
This allows for much faster pruning in some cases.

# Map Generation
For the paper, two types of random maps where generated as can be found in src/util/map_generation/map_generation.py.
- Mazes: generated with min-distance = 0 and otherwise default parameters.
- Obstacles: generated with min-distance = 0, max-neighbours = 3, open-factor = 0.65 and otherwise default parameters.

# Result files
## A*-ID-OD results
The results of each run benchmark map are stored in a file in [results](results).
The files for A*-ID-OD are stored per version of the algorithm where E or H indicates Exhaustive matching or heuristic matching and the other options indicate which things were or were not enabled.
The format of the files is as follows:
~~~
<benchmark set>, <map name>, <runtime>
~~~

Where benchmark set is the name of the folder that the benchmarks were stored in.
This allows for easy grouping of benchmarks to calculate averages and such.

## Other results

# Benchmark files
The benchmarks used for the paper can be found in [benchmarks/final.zip](benchmarks/final.zip)