def translate(): # POST /translate
    print("Translating pattern")
    return json.dumps({
        'success': True,
        'result': {}
    }, indent=4)



def get_lexicon(): # GET /lexicon/get
    print("Sending lexicon")
    pats = json.load(open('data/lexicon_list.json'))
    return json.dumps({
        'patterns': pats
    })

def get_lexicon_by_id(): # GET /lexicon/get-named?id=xyz
    print("Sending pattern from lexicon by ID")
    pats = json.load(open('data/lexicon.json'))
    try:
        return json.dumps({"success": True, "result": pats[request.args.get('id')]})
    except:
        print("Error: Pattern not found")
        return json.dumps({"success": False, "error": "Pattern not found in lexicon"})

def create_pattern(): # POST /patterns/create
    success = False
    size = regexes_converts.sizer("bo$23bo$3o4b!")
    print(size)
    newPattern = {
        # "hash": compiler.hasher(request.form["name"] + request.form["rle"]),
        # "name": request.form["name"],
        # "creator_name": request.form["creator_name"],
        "xbound": 0,
        "ybound": 0,
        # "rle": request.form["rle"]
    }
    return json.dumps({"success": success})


def get_pattern_by_id(): # GET /patterns/get-named?id=xyz
    print("Sending pattern by ID")
    pats = json.load(open('data/patterns.json'))
    try:
        return json.dumps({"success": True, "result": pats[request.args.get('id')]})
    except:
        print("Error: Pattern not found")
        return json.dumps({"success": False, "error": "Pattern not found"})

def get_patterns(): # GET /patterns/get
    print("Sending patterns")
    pats = json.load(open('data/patterns_list.json'))
    return json.dumps({
        'patterns': pats
    })

def status(): # GET /status
    print("Status: OK")
    return '{"status":"OK"}'
