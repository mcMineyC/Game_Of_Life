import json, compiler

lexicon_file = open("lexicon.txt", 'r')
lexicon_str = lexicon_file.read()
lexicon_file.close()

compiler.format_lexicon(input=lexicon_str, output_file="lexicon.json")
f_in = open("lexicon.json", 'r')
lexicon = json.load(f_in)
f_in.close()
lexicon_list = compiler.compile_to_list(lexicon)
f_out = open("lexicon_list.json", 'w')
json.dump(lexicon_list, f_out, indent=4)
f_out.close()

f_out = open("lexicon.jsonl", 'w')
f_out.write(compiler.compile_to_jsonl(lexicon_list))
f_out.close()