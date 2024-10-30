#include "compiler.h"
#include "cpp_lib/compile_functions.h"
#include <iostream>
#include <fstream>
#include <json/json.h>

void compile() {
    // Read lexicon.txt
    std::ifstream lexicon_file("data/lexicon.txt");
    if (!lexicon_file.is_open()) {
        std::cerr << "Error opening lexicon.txt" << std::endl;
        return;
    }
    std::string lexicon_str((std::istreambuf_iterator<char>(lexicon_file)), std::istreambuf_iterator<char>());
    lexicon_file.close();

    // Format lexicon and write to lexicon.json
    format_lexicon(lexicon_str, "data/lexicon.json");

    // Read lexicon.json
    std::ifstream f_in("data/lexicon.json");
    if (!f_in.is_open()) {
        std::cerr << "Error opening lexicon.json" << std::endl;
        return;
    }
    Json::Value lexicon;
    f_in >> lexicon;
    f_in.close();

    // Compile to list and write to lexicon_list.json
    std::unordered_map<std::string, std::unordered_map<std::string, std::string>> lexicon_map;
    for (const auto& key : lexicon.getMemberNames()) {
        for (const auto& subkey : lexicon[key].getMemberNames()) {
            lexicon_map[key][subkey] = lexicon[key][subkey].asString();
        }
    }
    auto lexicon_list = compile_to_list(lexicon_map);
    std::ofstream f_out("data/lexicon_list.json");
    if (!f_out.is_open()) {
        std::cerr << "Error opening lexicon_list.json" << std::endl;
        return;
    }
    Json::Value lexicon_list_json(Json::arrayValue);
    for (const auto& item : lexicon_list) {
        Json::Value item_json;
        for (const auto& pair : item) {
            item_json[pair.first] = pair.second;
        }
        lexicon_list_json.append(item_json);
    }
    f_out << Json::StyledWriter().write(lexicon_list_json);
    f_out.close();

    // Compile to JSONL and write to lexicon.jsonl
    f_out.open("data/lexicon.jsonl");
    if (!f_out.is_open()) {
        std::cerr << "Error opening lexicon.jsonl" << std::endl;
        return;
    }
    f_out << compile_to_jsonl(lexicon_map);
    f_out.close();

    // Read patterns.json
    f_in.open("data/patterns.json");
    if (!f_in.is_open()) {
        std::cerr << "Error opening patterns.json" << std::endl;
        return;
    }
    Json::Value patterns;
    f_in >> patterns;
    f_in.close();

    // Compile to list and write to patterns_list.json
    std::unordered_map<std::string, std::unordered_map<std::string, std::string>> patterns_map;
    for (const auto& key : patterns.getMemberNames()) {
        for (const auto& subkey : patterns[key].getMemberNames()) {
            patterns_map[key][subkey] = patterns[key][subkey].asString();
        }
    }
    auto patterns_list = compile_to_list(patterns_map);
    f_out.open("data/patterns_list.json");
    if (!f_out.is_open()) {
        std::cerr << "Error opening patterns_list.json" << std::endl;
        return;
    }
    Json::Value patterns_list_json(Json::arrayValue);
    for (const auto& pattern : patterns_list) {
        Json::Value pattern_json;
        for (const auto& pair : pattern) {
            pattern_json[pair.first] = pair.second;
        }
        patterns_list_json.append(pattern_json);
    }
    f_out << Json::StyledWriter().write(patterns_list_json);
    f_out.close();

    // Compile to JSONL and write to patterns.jsonl
    f_out.open("data/patterns.jsonl");
    if (!f_out.is_open()) {
        std::cerr << "Error opening patterns.jsonl" << std::endl;
        return;
    }
    
    f_out << compile_to_jsonl(patterns_map);
    f_out.close();
}

int main() {
    compile();
    return 0;
}