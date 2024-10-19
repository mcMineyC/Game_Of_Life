from regexes_converts import grid_paragraph_regex, txt_to_matrix, matrix_to_RLE, easy_RLE_to_txt, txt_to_RLE, RLE_to_matrix, matrix_to_txt

lex_file = open('lexicon.txt')
lexicontents = lex_file.read()
lex_file.close()
lexicon_paragraphs = grid_paragraph_regex.findall(lexicontents)

counter = 0
for paragraph in lexicon_paragraphs:
    counter += 1
    pattern_name = paragraph[0]
    original_plaintext = paragraph[2]
    cooked_plaintext1 = easy_RLE_to_txt(matrix_to_RLE(txt_to_matrix(original_plaintext)))
    cooked_plaintext2 = matrix_to_txt(RLE_to_matrix(txt_to_RLE(original_plaintext)))
    assert original_plaintext == cooked_plaintext1, 'Conversion glitch!\n%s\n%s\nis not equal to\n%s\nitem == %s' % (pattern_name, original_plaintext, cooked_plaintext1, counter)