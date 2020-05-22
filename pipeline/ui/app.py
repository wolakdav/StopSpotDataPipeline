from flask import Flask, render_template, request
import sys
import os
import json
from flask import jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
        return render_template('index.html')


@app.route('/config', methods = ['GET', 'POST'])
def config():
        if request.method == 'POST':
                f = open('../assets/config.json', 'w')
                request_json = request.get_json()
                f.write(json.dumps(request_json, indent=4))
                f.close()
                return jsonify({'status': 'success'})
 
        else:
                f = open('../assets/config.json')
                config_json = json.load(f)

                return jsonify(config_json)


@app.route('/log')
def log():
        f = open('../output/log.txt')
        
        return f.read()

@app.route('/shutdown')
def shutdown_ui():
        print('Shutting down StopSpot UI...')

        #Flask catches SystemExit exceptions so os._exit is necessary for the Docker to exit
        os._exit(2)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
