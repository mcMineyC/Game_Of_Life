#include "cpp_lib/compile_functions.h"
#include "cpp_lib/regexes.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <json/json.h>
#include <openssl/md5.h>

// Function definitions
std::string hasher(const std::string& MD5Input) {
    unsigned char digest[MD5_DIGEST_LENGTH];
    MD5((unsigned char*)MD5Input.c_str(), MD5Input.size(), (unsigned char*)&digest);
    char mdString[33];
    for (int i = 0; i < 16; ++i)
        sprintf(&mdString[i * 2], "%02x", (unsigned int)digest[i]);
    return std::string(mdString);
}

void format_lexicon(const std::string& input, const std::string& output_file) {
    // Store contents of lexicon.txt to lexicon_array.json with proper formatting
    // Search lexicon
    std::smatch match;
    std::vector<std::vector<std::string>> lexicon_paragraphs;
    std::string::const_iterator searchStart(input.cbegin());
    while (std::regex_search(searchStart, input.cend(), match, grid_paragraph_regex)) {
        lexicon_paragraphs.push_back({match[1], match[2], match[3]});
        searchStart = match.suffix().first;
    }

    // Convert to desired format
    Json::Value json_master_library;
    for (const auto& paragraph : lexicon_paragraphs) {
        auto formatted = convert_lexicon(paragraph);
        json_master_library[formatted["hash"]] = formatted;
    }

    // Write to lexicon_array.json
    std::ofstream json_file(output_file);
    json_file << json_master_library.toStyledString();
    json_file.close();
}

std::unordered_map<std::string, std::string> convert_lexicon(const std::vector<std::string>& paragraph) {
    std::string rle = txt_to_RLE(paragraph[2]);
    std::string raw_rle = rle.substr(rle.find("\n") + 1);
    std::string name = paragraph[0];
    std::string hash = hasher(name + rle);
    std::string creator = "LifeWiki Lexicon";
    std::smatch match;
    std::regex_search(rle, match, RLE_regex);
    std::string x = match[3];
    std::string y = match[4];
    auto comments = comment_to_dict(match[1]);

    return {
        {"hash", hash},
        {"name", name},
        {"creator", creator},
        {"xbounds", x},
        {"ybounds", y},
        {"rle", raw_rle},
        {"raw_rle", rle},
        {"comments", comments}
    };
}

std::vector<std::unordered_map<std::string, std::string>> compile_to_list(const std::unordered_map<std::string, std::unordered_map<std::string, std::string>>& input_dict) {
    // Converts the lexicon from a dictionary to a list
    // This is for the frontend to use
    std::vector<std::unordered_map<std::string, std::string>> result;
    for (const auto& item : input_dict) {
        result.push_back(item.second);
    }
    return result;
}

std::string compile_to_jsonl(const std::unordered_map<std::string, std::unordered_map<std::string, std::string>>& input_dict) {
    // Converts the lexicon from a dictionary to a jsonl file
    // This is for the backend to use
    std::ostringstream jsonl;
    for (const auto& item : input_dict) {
        Json::Value json_item;
        json_item["id"] = item.second.at("hash");
        json_item["hash"] = item.second.at("hash");
        json_item["name"] = item.second.at("name");
        json_item["creator"] = item.second.at("creator");
        json_item["xbounds"] = item.second.at("xbounds");
        json_item["ybounds"] = item.second.at("ybounds");
        json_item["raw_rle"] = item.second.at("raw_rle");
        json_item["rle"] = item.second.at("rle");
        json_item["comments"] = item.second.at("comments");

        jsonl << json_item.toStyledString() << "\n";
    }
    return jsonl.str();
}