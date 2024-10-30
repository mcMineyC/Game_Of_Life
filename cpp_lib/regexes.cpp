#include "regexes.h"
#include <iostream>

// Global variables
const std::vector<char> digits = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'};
const std::vector<std::vector<bool>> empty_chunk(8, std::vector<bool>(8, false));

// Regular expressions
const std::regex grid_paragraph_regex(R"(\n:([^\t\n:]+):([^\t\n]+\n)*((\t[\*\.]{2,}\n)+))");
const std::regex grid_regex(R"(((\t[\*\.]{2,}\n)+))");
const std::regex line_regex(R"(\t?([\*\.]{2,})\n)");
const std::regex whitespace_regex(R"(\s)");
const std::regex RLE_regex(R"(^\s?((#.+\n)*)x = ([0-9]+), y = ([0-9]+), rule = B3/S23\n([0-9bo\$\s]+!)\s?$)", std::regex_constants::icase);
const std::string default_RLE_comment = "#C [[ ZOOM 7 GRID COLOR GRID 31 31 31 COLOR DEADRAMP 31 0 0 COLOR ALIVE 255 255 255 COLOR ALIVERAMP 255 255 255 COLOR DEAD 0 0 47 COLOR BACKGROUND 0 0 0 GPS 10 WIDTH 937 HEIGHT 600 ]]";
const std::regex comment_regex(R"(#C \[\[ .+ \]\])");
const std::regex comment_items_regex(R"(([A-Z ]+) ([0-9 ]+)|([A-Z][a-z]+))");
const std::regex greedy_regex(R"(\$+)");

// Function definitions
void regexes() {
    std::cout << "Regexes are loaded." << std::endl;
}