from flask import Flask, request
from flask_cors import CORS, cross_origin
import json, typesense

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




if __name__ == '__main__':
    app.run(port=port,debug=True)