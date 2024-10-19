import json
from lib import compile_functions
lexicon_file = open("data/lexicon.txt", 'r')
lexicon_str = lexicon_file.read()
lexicon_file.close()

compile_functions.format_lexicon(input=lexicon_str, output_file="data/lexicon.json")
f_in = open("data/lexicon.json", 'r')
lexicon = json.load(f_in)
f_in.close()
lexicon_list = compile_functions.compile_to_list(lexicon)
f_out = open("data/lexicon_list.json", 'w')
json.dump(lexicon_list, f_out, indent=4)
f_out.close()

f_out = open("data/lexicon.jsonl", 'w')
f_out.write(compile_functions.compile_to_jsonl(lexicon_list))
f_out.close()


f_in = open("data/patterns.json", 'r')
patterns = json.load(f_in)
f_in.close()
patterns_list = compile_functions.compile_to_list(patterns)
f_out = open("data/patterns_list.json", 'w')
json.dump(patterns_list, f_out, indent=4)
f_out.close()

f_out = open("data/patterns.jsonl", 'w')
f_out.write(compile_functions.compile_to_jsonl(patterns_list))
f_out.close()
