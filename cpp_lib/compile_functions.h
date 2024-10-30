#ifndef COMPILE_FUNCTIONS_H
#define COMPILE_FUNCTIONS_H

#include <string>
#include <unordered_map>
#include <vector>

// Function declarations
std::string hasher(const std::string& MD5Input);
void format_lexicon(const std::string& input, const std::string& output_file);
std::unordered_map<std::string, std::string> convert_lexicon(const std::vector<std::string>& paragraph);
std::vector<std::unordered_map<std::string, std::string>> compile_to_list(const std::unordered_map<std::string, std::unordered_map<std::string, std::string>>& input_dict);
std::string compile_to_jsonl(const std::unordered_map<std::string, std::unordered_map<std::string, std::string>>& input_dict);

#endif // COMPILE_FUNCTIONS_H