from flask import Flask, render_template, request
import sys
import os
import json
from flask import jsonify
from datetime import date
app = Flask(__name__)

@app.route('/')
def index():
        return render_template('index.html')


@app.route('/config', methods = ['GET', 'POST'])
def config():
        if request.method == 'POST':
                try:
                        request_json = request.get_json()
                except Exception:
                        return jsonify({'status': 'fail'})

                f = open('../assets/config.json', 'w')
                f.write(json.dumps(request_json, indent=4, sort_keys=False))
                f.close()
                return jsonify({'status': 'success'})
 
        else:
                f = open('../assets/config.json')
                config_json = json.load(f)

                return jsonify(config_json)


@app.route('/log')
def log():
        today = date.today().strftime('%Y-%m-%d')
        filename = today + '.txt'
        
        try:
                f = open('../output/' + filename)
                return f.read()

        except FileNotFoundError:
                return 'Log file not found for {}.'.format(today)

@app.route('/shutdown')
def shutdown_ui():
        print('Shutting down StopSpot UI...')

        #Flask catches SystemExit exceptions so os._exit is necessary for the Docker to exit
        os._exit(2)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
