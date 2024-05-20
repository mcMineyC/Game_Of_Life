from flask import Flask
from flask_cors import CORS, cross_origin
import json

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
    pats = json.load(open('lexicon_list.json'))
    return json.dumps({
        'patterns': pats
    })

if __name__ == '__main__':
    app.run(port=port,debug=True)