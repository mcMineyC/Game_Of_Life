import json, hashlib
from regexes_converts import grid_paragraph_regex, txt_to_RLE, RLE_regex, comment_to_dict
#TODO fix import here

def hasher(MD5Input):
    return hashlib.md5(MD5Input.encode()).hexdigest()

def format_lexicon(input, output_file):
    #store contents of lexicon.txt to lexicon_array.json with proper formatting
    #search lexicon
    lexicon_paragraphs = grid_paragraph_regex.findall(input)

    #convert to desired Python format
    json_master_library = {}
    for paragraph in lexicon_paragraphs:
         formatted = convert_lexicon(paragraph)
         json_master_library[formatted["hash"]] = formatted
    
    #write to lexicon_array.json
    json_str = json.dumps(json_master_library, indent=4)
    json_file = open(output_file, 'w')
    json_file.write(json_str)
    json_file.close()

def convert_lexicon(paragraph):
        rle = txt_to_RLE(paragraph[2])
        raw_rle = rle.split("\n")[2]
        name = paragraph[0]
        hash = hasher(name + rle) #why is hash blue? TODO fix this and input as well?
        creator = "LifeWiki Lexicon"
        xy = RLE_regex.findall(rle)
        x = xy[0][2]
        y = xy[0][3]
        comments = comment_to_dict(xy[0][1])
        return {
            "hash": hash,
            "name": name,
            "creator": creator,
            "xbounds": x,
            "ybounds": y,
            "rle": raw_rle,
            "raw_rle": rle,
            "comments": comments,
       }

def compile_to_list(input_dict):
    #converts the lexicon from a dictionary to a list
    #this is for the frontend to use
    return [input_dict[key] for key in input_dict]

def compile_to_jsonl(input_dict):
    #converts the lexicon from a dictionary to a jsonl file
    #this is for the backend to use
    jsonl = ""
    for item in input_dict:
        jsonl += json.dumps({
            "id": item["hash"],
            "hash": item["hash"],
            "name": item["name"],
            "creator": item["creator"],
            "xbounds": item["xbounds"],
            "ybounds": item["ybounds"],
            "raw_rle": item["raw_rle"], #this is the full RLE, not just the pattern
            "rle": item["rle"],
            "comments": json.dumps(item["comments"])
        }) + "\n"
    return jsonl