from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO
import json, typesense
import multiprocessing as mp
# from lib import convert_functions

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
socketio = SocketIO(app, cors_allowed_origins="*")
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
    pats = json.load(open('data/patterns_list.json'))
    return json.dumps({
        'patterns': pats
    })

@app.route('/patterns/get-named')
@cross_origin()
def get_pattern_by_id():
    print("Sending pattern by ID")
    pats = json.load(open('data/patterns.json'))
    try:
        return json.dumps({"success": True, "result": pats[request.args.get('id')]})
    except:
        print("Error: Pattern not found")
        return json.dumps({"success": False, "error": "Pattern not found"})

@app.route('/patterns/create', methods=["POST", "GET"])
@cross_origin()
def create_pattern():
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

@app.route('/lexicon/get-named')
@cross_origin()
def get_lexicon_by_id():
    print("Sending pattern from lexicon by ID")
    pats = json.load(open('data/lexicon.json'))
    try:
        return json.dumps({"success": True, "result": pats[request.args.get('id')]})
    except:
        print("Error: Pattern not found")
        return json.dumps({"success": False, "error": "Pattern not found in lexicon"})

@app.route('/lexicon/get')
@cross_origin()
def get_lexicon():
    print("Sending lexicon")
    pats = json.load(open('data/lexicon_list.json'))
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

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    socketio.emit('response', 'Server received your message: ' + data)
@socketio.on("json")
def handle_json(data):
    print('Received json:', data)
    data["recevied"] = True
    socketio.emit('responseJSON', data)

if __name__ == '__main__':
    socketio.run(app, port=port, host="0.0.0.0", debug=True)
