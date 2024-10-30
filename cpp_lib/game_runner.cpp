#include "game_runner.h"
#include <iostream>
#include <chrono>
#include <cstring>
#include <boost/functional/hash.hpp>

// Define the empty chunk as a global constant
const Chunk empty_chunk(8, std::vector<bool>(8, false));

// Converts relative position to absolute position
std::pair<int, int> get_abs_position(const std::pair<int, int>& chunk, int x, int y) {
    return {chunk.first * 8 + x, chunk.second * 8 + y};
}

// Converts absolute position to relative position
std::tuple<std::pair<int, int>, int, int> get_rltv_position(int x, int y) {
    return {{x / 8, y / 8}, x % 8, y % 8};
}

// Find the states of all 8 cells surrounding this one
std::pair<std::vector<bool>, Grid> get_srnd_cells(const std::pair<int, int>& pos, bool is_new, const Grid& master_grid) {
    int x = pos.first;
    int y = pos.second;

    std::vector<bool> output;
    Grid new_chunks;

    std::vector<std::pair<int, int>> positions = {{-1, 1}, {0, 1}, {1, 1}, {-1, 0}, {1, 0}, {-1, -1}, {0, -1}, {1, -1}};
    for (const auto& p : positions) {
        auto [chunk, rel_x, rel_y] = get_rltv_position(x + p.first, y + p.second);
        try {
            output.push_back(master_grid.at(chunk)[rel_x][rel_y]);
        } catch (const std::out_of_range&) {
            output.push_back(false);
            auto [cell_chunk, cell_x, cell_y] = get_rltv_position(x, y);
            if (master_grid.at(cell_chunk)[cell_x][cell_y] && !is_new) {
                new_chunks[chunk] = empty_chunk;
            }
        }
    }

    return {output, new_chunks};
}

// Accepts state of a cell along with the states of its 8 neighbors; returns new state for cell
bool cell_next_day(bool cell_state, const std::vector<bool>& surrounding_cells) {
    int live_count = std::count(surrounding_cells.begin(), surrounding_cells.end(), true);
    if (cell_state) {
        return live_count == 2 || live_count == 3;
    } else {
        return live_count == 3;
    }
}

// Accepts full grid and returns the next generation of the grid
Grid next_gen(Grid input_grid) {
    Grid output_grid;
    auto start_time = std::chrono::high_resolution_clock::now();

    // Remove empty chunks from input_grid
    for (auto it = input_grid.begin(); it != input_grid.end();) {
        if (it->second == empty_chunk) {
            it = input_grid.erase(it);
        } else {
            ++it;
        }
    }

    Grid new_chunks;

    for (const auto& [chunk, cells] : input_grid) {
        output_grid[chunk] = Chunk(8, std::vector<bool>(8, false));
        for (int x = 0; x < 8; ++x) {
            for (int y = 0; y < 8; ++y) {
                auto [surrounding_cells, any_new_chunks] = get_srnd_cells(get_abs_position(chunk, x, y), false, input_grid);
                new_chunks.insert(any_new_chunks.begin(), any_new_chunks.end());
                output_grid[chunk][x][y] = cell_next_day(input_grid[chunk][x][y], surrounding_cells);
            }
        }
    }

    for (const auto& [chunk, cells] : new_chunks) {
        input_grid[chunk] = cells;
    }

    for (const auto& [chunk, cells] : new_chunks) {
        output_grid[chunk] = Chunk(8, std::vector<bool>(8, false));
        for (int x = 0; x < 8; ++x) {
            for (int y = 0; y < 8; ++y) {
                auto surrounding_cells = get_srnd_cells(get_abs_position(chunk, x, y), true, input_grid).first;
                output_grid[chunk][x][y] = cell_next_day(input_grid[chunk][x][y], surrounding_cells);
            }
        }
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;
    std::cout << "Time taken: " << elapsed.count() << " seconds" << std::endl;

    return output_grid;
}