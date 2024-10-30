#include "convert_functions.h"
#include "regexes.h"
#include <iostream>
#include <regex>
#include <unordered_map>
#include <vector>
#include <cassert>

// Function definitions

std::string easy_RLE_to_txt(const std::string& erttRLE) {
    std::smatch match;
    if (std::regex_search(erttRLE, match, RLE_regex)) {
        int x = std::stoi(match[3]);
        int y = std::stoi(match[4]);
        std::string rle = match[5];
        std::string rle_no_ws;
        for (char c : rle) {
            if (c != '\n' && c != '\t' && c != ' ') {
                rle_no_ws += c;
            }
        }
        return advanced_RLE_to_txt(x, y, rle_no_ws);
    }
    return "";
}

std::string advanced_RLE_to_txt(int arttXBound, int arttYBound, const std::string& arttRLE) {
    std::string arttOutput;
    std::string arttInt;
    int arttCharsInLine = 0;

    for (char c : arttRLE) {
        if (c == '\n' || c == '\t' || c == ' ') {
            continue;
        }
        if (std::isdigit(c)) {
            arttInt += c;
        } else if (c == '$') {
            if (arttInt.empty()) arttInt = "1";
            for (int i = 0; i < std::stoi(arttInt); ++i) {
                arttOutput += std::string(arttXBound - arttCharsInLine, '.') + '\n';
                arttCharsInLine = 0;
            }
            arttInt.clear();
        } else if (c == '!') {
            arttOutput += std::string(arttXBound - arttCharsInLine, '.') + '\n';
            break;
        } else {
            char arttState = (c == 'b') ? '.' : '*';
            if (arttInt.empty()) arttInt = "1";
            arttOutput += std::string(std::stoi(arttInt), arttState);
            arttCharsInLine += std::stoi(arttInt);
            arttInt.clear();
        }
    }

    std::vector<std::string> arttOutputLines;
    std::smatch match;
    std::string::const_iterator searchStart(arttOutput.cbegin());
    while (std::regex_search(searchStart, arttOutput.cend(), match, line_regex)) {
        arttOutputLines.push_back(match[1]);
        searchStart = match.suffix().first;
    }

    assert(arttOutputLines.size() == arttYBound);
    for (const auto& line : arttOutputLines) {
        assert(line.size() == arttXBound);
    }

    return arttOutput.substr(0, arttOutput.size() - 1); // remove extra '\n' at the end of str
}

std::string matrix_to_txt(const std::unordered_map<std::pair<int, int>, std::vector<std::vector<bool>>>& mttGrid) {
    int mttUpMost = mttGrid.begin()->first.second;
    int mttDownMost = mttGrid.begin()->first.second;
    int mttLeftMost = mttGrid.begin()->first.first;
    int mttRightMost = mttGrid.begin()->first.first;

    for (const auto& chunk : mttGrid) {
        if (chunk.first.second > mttUpMost) mttUpMost = chunk.first.second;
        if (chunk.first.second < mttDownMost) mttDownMost = chunk.first.second;
        if (chunk.first.first > mttRightMost) mttRightMost = chunk.first.first;
        if (chunk.first.first < mttLeftMost) mttLeftMost = chunk.first.first;
    }

    int mttHeight = (mttUpMost - mttDownMost + 1) * 8;
    int mttWidth = (mttRightMost - mttLeftMost + 1) * 8;

    std::vector<std::vector<char>> mttOutput(mttWidth, std::vector<char>(mttHeight, '.'));

    for (const auto& chunk : mttGrid) {
        std::pair<int, int> mttZeroedChunk = {chunk.first.first - mttLeftMost, chunk.first.second - mttDownMost};
        for (int x = 0; x < 8; ++x) {
            for (int y = 0; y < 8; ++y) {
                if (chunk.second[x][y]) {
                    try {
                        mttOutput[mttZeroedChunk.first * 8 + x][mttZeroedChunk.second * 8 + y] = '*';
                    } catch (const std::out_of_range&) {
                        std::cerr << "IndexError. These coords out of range: " << chunk.first.first * 8 + x << " " << chunk.first.second * 8 + y << std::endl;
                    }
                }
            }
        }
    }

    std::string mttOutputStr;
    for (int y = mttOutput[0].size() - 1; y >= 0; --y) {
        for (int x = 0; x < mttOutput.size(); ++x) {
            mttOutputStr += mttOutput[x][y];
        }
        mttOutputStr += '\n';
    }

    return mttOutputStr.substr(0, mttOutputStr.size() - 1); // shave final '\n'
}

std::string txt_to_RLE(const std::string& ttrInput, const std::string& ttrComment) {
    std::string ttrInputWithNewline = ttrInput + '\n';
    std::vector<std::string> ttrLines;
    std::smatch match;
    std::string::const_iterator searchStart(ttrInputWithNewline.cbegin());
    while (std::regex_search(searchStart, ttrInputWithNewline.cend(), match, line_regex)) {
        ttrLines.push_back(match[1]);
        searchStart = match.suffix().first;
    }

    int ttrHeight = ttrLines.size();
    int ttrWidth = ttrLines[0].size();
    for (const auto& line : ttrLines) {
        assert(line.size() == ttrWidth);
    }

    std::string ttrOutputRLE;
    for (const auto& line : ttrLines) {
        std::pair<char, int> ttrRun = {line[0], 0};
        for (char cell : line) {
            if (cell == ttrRun.first) {
                ttrRun.second++;
            } else {
                char ttrState = (ttrRun.first == '.') ? 'b' : 'o';
                ttrOutputRLE += (ttrRun.second == 1) ? std::string(1, ttrState) : std::to_string(ttrRun.second) + ttrState;
                ttrRun = {cell, 1};
            }
        }
        if (ttrRun.first == '*') {
            ttrOutputRLE += (ttrRun.second == 1) ? "o" : std::to_string(ttrRun.second) + "o";
        }
        ttrOutputRLE += '$';
    }
    ttrOutputRLE.back() = '!';

    std::vector<std::string> ttrDollars;
    searchStart = ttrOutputRLE.cbegin();
    while (std::regex_search(searchStart, ttrOutputRLE.cend(), match, greedy_regex)) {
        ttrDollars.push_back(match[0]);
        searchStart = match.suffix().first;
    }

    int ttrDollarCount = 0;
    for (const auto& instance : ttrDollars) {
        if (instance.size() > ttrDollarCount) ttrDollarCount = instance.size();
    }

    for (int len = ttrDollarCount; len > 1; --len) {
        std::regex dollarSub(std::string(len, '$'));
        ttrOutputRLE = std::regex_replace(ttrOutputRLE, dollarSub, std::to_string(len) + '$');
    }

    std::string ttrOutputHeader = "x = " + std::to_string(ttrWidth) + ", y = " + std::to_string(ttrHeight) + ", rule = B3/S23\n";
    return ttrComment + ttrOutputHeader + ttrOutputRLE;
}

std::unordered_map<std::string, std::string> comment_to_dict(const std::string& ctdInput) {
    std::smatch match;
    std::regex_search(ctdInput, match, comment_regex);
    std::string ctdTheComment = match[0];
    std::vector<std::vector<std::string>> ctdCommentItems;
    searchStart = ctdTheComment.cbegin();
    while (std::regex_search(searchStart, ctdTheComment.cend(), match, comment_items_regex)) {
        ctdCommentItems.push_back({match[1], match[2], match[3]});
        searchStart = match.suffix().first;
    }

    std::vector<std::vector<std::string>> ctdList4Output;
    for (const auto& item : ctdCommentItems) {
        ctdList4Output.push_back({item[0]});
        if (!item[1].empty()) {
            ctdList4Output.back().push_back("");
            std::string ctdInt;
            for (char c : item[1]) {
                if (std::isdigit(c)) {
                    ctdInt += c;
                } else {
                    ctdList4Output.back().back() += ctdInt;
                    ctdInt.clear();
                }
            }
        } else {
            ctdList4Output.back().push_back(item[2]);
        }
    }

    if (ctdList4Output[0][0][0] == ' ') {
        ctdList4Output[0][0] = ctdList4Output[0][0].substr(1);
    }

    for (auto& item : ctdList4Output) {
        item[0] = std::regex_replace(item[0], std::regex(" "), "_");
        if (item[1].size() == 1) {
            item[1] = item[1][0];
        }
    }

    std::unordered_map<std::string, std::string> ctdOutput;
    for (const auto& item : ctdList4Output) {
        ctdOutput[item[0]] = item[1];
    }
    return ctdOutput;
}

std::unordered_map<std::pair<int, int>, std::vector<std::vector<bool>>> txt_to_matrix(const std::string& ttmGrid) {
    std::string ttmGridWithNewline = ttmGrid + '\n';
    std::vector<std::string> ttmGridLines;
    std::smatch match;
    std::string::const_iterator searchStart(ttmGridWithNewline.cbegin());
    while (std::regex_search(searchStart, ttmGridWithNewline.cend(), match, line_regex)) {
        ttmGridLines.push_back(match[1]);
        searchStart = match.suffix().first;
    }
    std::reverse(ttmGridLines.begin(), ttmGridLines.end());

    int ttmCellWidth = ttmGridLines[0].size();
    int ttmCellHeight = ttmGridLines.size();
    int ttmChunkWidth = (ttmCellWidth % 8 == 0) ? ttmCellWidth / 8 : ttmCellWidth / 8 + 1;
    int ttmChunkHeight = (ttmCellHeight % 8 == 0) ? ttmCellHeight / 8 : ttmCellHeight / 8 + 1;

    std::unordered_map<std::pair<int, int>, std::vector<std::vector<bool>>> ttmOutGrid;
    for (int chunkY = 0; chunkY < ttmChunkHeight; ++chunkY) {
        for (int chunkX = 0; chunkX < ttmChunkWidth; ++chunkX) {
            std::vector<std::vector<bool>> chunk(8, std::vector<bool>(8, false));
            for (int cellY = 0; cellY < 8; ++cellY) {
                for (int cellX = 0; cellX < 8; ++cellX) {
                    try {
                        chunk[cellX][cellY] = (ttmGridLines[chunkY * 8 + cellY][chunkX * 8 + cellX] == '*');
                    } catch (const std::out_of_range&) {
                        chunk[cellX][cellY] = false;
                    }
                }
            }
            if (chunk != empty_chunk) {
                ttmOutGrid[{chunkX, chunkY}] = chunk;
            }
        }
    }
    return ttmOutGrid;
}

std::unordered_map<std::pair<int, int>, std::vector<std::vector<bool>>> RLE_to_matrix(const std::string& rtmInput) {
    return txt_to_matrix(easy_RLE_to_txt(rtmInput));
}

std::string matrix_to_RLE(const std::unordered_map<std::pair<int, int>, std::vector<std::vector<bool>>>& mtrMatrix, const std::string& mtrComment) {
    return txt_to_RLE(matrix_to_txt(mtrMatrix), mtrComment);
}

void pro_print_grid(const std::unordered_map<std::pair<int, int>, std::vector<std::vector<bool>>>& ppgGrid, const std::pair<int, int>& ppgUpLeft, const std::pair<int, int>& ppgDownRight) {
    std::string ppgOutput;
    for (const auto& chunkRow : get_chunk_window(ppgUpLeft, ppgDownRight)) {
        for (int cellRow = 7; cellRow >= 0; --cellRow) {
            for (const auto& chunk : chunkRow) {
                for (int x = 0; x < 8; ++x) {
                    if (ppgGrid.find(chunk) != ppgGrid.end()) {
                        ppgOutput += (ppgGrid.at(chunk)[x][cellRow] ? "[]" : "<>");
                    } else {
                        ppgOutput += "::";
                    }
                }
            }
            ppgOutput += '\n';
        }
    }
    std::cout << ppgOutput;
}

std::string grid_to_string(const std::unordered_map<std::pair<int, int>, std::vector<std::vector<bool>>>& gtsGrid, const std::pair<int, int>& gtsUpLeft, const std::pair<int, int>& gtsDownRight) {
    std::string gtsOutput;
    for (const auto& chunkRow : get_chunk_window(gtsUpLeft, gtsDownRight)) {
        for (int cellRow = 7; cellRow >= 0; --cellRow) {
            for (const auto& chunk : chunkRow) {
                for (int x = 0; x < 8; ++x) {
                    if (gtsGrid.find(chunk) != gtsGrid.end()) {
                        gtsOutput += (gtsGrid.at(chunk)[x][cellRow] ? '1' : '0');
                    } else {
                        gtsOutput += '0';
                    }
                }
            }
            gtsOutput += '\n';
        }
    }
    return gtsOutput;
}

std::vector<std::vector<std::pair<int, int>>> get_chunk_window(const std::pair<int, int>& gcwUpLeft, const std::pair<int, int>& gcwDownRight) {
    assert(gcwUpLeft.first <= gcwDownRight.first && gcwUpLeft.second >= gcwDownRight.second);
    std::vector<std::vector<std::pair<int, int>>> gcwOutput;
    for (int y = gcwUpLeft.second; y >= gcwDownRight.second; --y) {
        std::vector<std::pair<int, int>> row;
        for (int x = gcwUpLeft.first; x <= gcwDownRight.first; ++x) {
            row.emplace_back(x, y);
        }
        gcwOutput.push_back(row);
    }
    assert(!gcwOutput.empty());
    return gcwOutput;
}