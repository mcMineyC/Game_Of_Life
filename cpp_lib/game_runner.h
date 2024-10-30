#ifndef GAME_RUNNER_H
#define GAME_RUNNER_H

#include <unordered_map>
#include <vector>
#include <utility>

// Type aliases for readability
using Chunk = std::vector<std::vector<bool>>;
using Grid = std::unordered_map<std::pair<int, int>, Chunk, boost::hash<std::pair<int, int>>>;

// Function declarations
Grid next_gen(Grid input_grid);

#endif // GAME_RUNNER_H