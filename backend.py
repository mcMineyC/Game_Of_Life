from flask import Flask, request
from flask_cors import CORS, cross_origin
import json, typesense
import regexes_converts

client = typesense.Client({
    'nodes': [{
        'host': '192.168.30.36',
        'port': '8108',
        'protocol': 'http'
    }],
    'api_key': 'xyz123',
    'connection_timeout_seconds': 2
})

port = 5000
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/status')
@cross_origin()
def status():
    print("Status: OK")
    return '{"status":"OK"}'

@app.route('/patterns/get')
@cross_origin()
def get_patterns():
    print("Sending patterns")
    pats = json.load(open('patterns_list.json'))
    return json.dumps({
        'patterns': pats
    })

@app.route('/patterns/get-named')
@cross_origin()
def get_pattern_by_id():
    print("Sending pattern by ID")
    pats = json.load(open('patterns.json'))
    try:
        return json.dumps({"success": True, "result": pats[request.args.get('id')]})
    except:
        print("Error: Pattern not found")
        return json.dumps({"success": False, "error": "Pattern not found"})


@app.route('/lexicon/get-named')
@cross_origin()
def get_lexicon_by_id():
    print("Sending pattern from lexicon by ID")
    pats = json.load(open('lexicon.json'))
    try:
        return json.dumps({"success": True, "result": pats[request.args.get('id')]})
    except:
        print("Error: Pattern not found")
        return json.dumps({"success": False, "error": "Pattern not found in lexicon"})

@app.route('/lexicon/get')
@cross_origin()
def get_lexicon():
    print("Sending lexicon")
    pats = json.load(open('lexicon_list.json'))
    return json.dumps({
        'patterns': pats
    })

@app.route('/lexicon/search')
@cross_origin()
def search_lexicon():
    print("Searching lexicon")
    r = client.collections['lexicon'].documents.search({
        'q': request.args.get('q'),
        'query_by': 'name',
    })
    results = r['hits']
    list = []
    for i in results:
        i['document']['comments'] = json.loads(i['document']['comments'])
        list.append(i['document'])
    return json.dumps({
        'patterns': list
    }, indent=4)

@app.route('/translate', methods=['POST'])
@cross_origin()
def translate():
    print("Translating pattern")
    return json.dumps({
        'success': True,
        'result': {}
    }, indent=4)


if __name__ == '__main__':
    app.run(port=port,debug=True)