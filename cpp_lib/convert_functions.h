#ifndef CONVERT_FUNCTIONS_H
#define CONVERT_FUNCTIONS_H

#include <string>
#include <unordered_map>
#include <vector>

// Function declarations
std::string easy_RLE_to_txt(const std::string& erttRLE);
std::string advanced_RLE_to_txt(int arttXBound, int arttYBound, const std::string& arttRLE);
std::string matrix_to_txt(const std::unordered_map<std::pair<int, int>, std::vector<std::vector<bool>>>& mttGrid);
std::string txt_to_RLE(const std::string& ttrInput, const std::string& ttrComment);
std::unordered_map<std::string, std::string> comment_to_dict(const std::string& ctdInput);
std::unordered_map<std::pair<int, int>, std::vector<std::vector<bool>>> txt_to_matrix(const std::string& ttmGrid);
std::unordered_map<std::pair<int, int>, std::vector<std::vector<bool>>> RLE_to_matrix(const std::string& rtmInput);
std::string matrix_to_RLE(const std::unordered_map<std::pair<int, int>, std::vector<std::vector<bool>>>& mtrMatrix, const std::string& mtrComment);
void pro_print_grid(const std::unordered_map<std::pair<int, int>, std::vector<std::vector<bool>>>& ppgGrid, const std::pair<int, int>& ppgUpLeft, const std::pair<int, int>& ppgDownRight);
std::string grid_to_string(const std::unordered_map<std::pair<int, int>, std::vector<std::vector<bool>>>& gtsGrid, const std::pair<int, int>& gtsUpLeft, const std::pair<int, int>& gtsDownRight);
std::vector<std::vector<std::pair<int, int>>> get_chunk_window(const std::pair<int, int>& gcwUpLeft, const std::pair<int, int>& gcwDownRight);

#endif // CONVERT_FUNCTIONS_H