#ifndef REGEXES_H
#define REGEXES_H

#include <regex>
#include <vector>
#include <string>

// Global variables
extern const std::vector<char> digits;
extern const std::vector<std::vector<bool>> empty_chunk;

// Regular expressions
extern const std::regex grid_paragraph_regex;
extern const std::regex grid_regex;
extern const std::regex line_regex;
extern const std::regex whitespace_regex;
extern const std::regex RLE_regex;
extern const std::string default_RLE_comment;
extern const std::regex comment_regex;
extern const std::regex comment_items_regex;
extern const std::regex greedy_regex;

// Function declarations
void regexes();

#endif // REGEXES_H