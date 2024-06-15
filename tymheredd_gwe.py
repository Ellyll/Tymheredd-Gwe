#!/usr/bin/python3

# TODO:
# make GET work
# proxy through apache?

# postgres:
# https://stackoverflow.com/questions/55523299/best-practices-for-persistent-database-connections-in-python-when-using-flask
# https://www.psycopg.org/docs/usage.html

from flask import Flask, json, jsonify, request, has_request_context
from flask_cors import CORS
from flask.logging import default_handler
import logging
import os
import re
from extensions import pgdb

app = Flask(__name__)
CORS(app)
pgdb.init_app(app)

# Format logging
class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)

formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s '
    '%(levelname)s in %(module)s: %(message)s'
)
default_handler.setFormatter(formatter)


# Authorisation stuff
valid_api_keys = os.environ["AUTHORISED_API_KEYS"].split(",")
auth_reg = re.compile(r"^Bearer\s+(\S+)$")

def has_valid_api_key(request): 
    if not "Authorization" in request.headers:
        return False
    auth = request.headers["Authorization"]
    if not auth_reg.match(auth):
        return False
    api_key = auth_reg.sub(r"\1", auth)
    if api_key in valid_api_keys:
        return True
    return False


# Routes

@app.route('/')
def index():
    return "Moo!"

@app.route('/api/tymheredd', methods=['GET'])
def tymheredd_get():
    # TODO: read from db
    with pgdb.get_cursor() as cur:
        cur.execute("SELECT amser, tymheredd, gwasgedd, golau_light, golau_lux FROM darlleniad ORDER BY amser DESC LIMIT 1")
        (amser, tymheredd, gwasgedd, golau_light, golau_lux) = cur.fetchone()
        data_dict = { "amser": amser.isoformat(), "tymheredd": tymheredd, "gwasgedd": gwasgedd, "golau_light": golau_light, "golau_lux": golau_lux }
        return jsonify(data_dict)

@app.route('/api/tymheredd', methods=['POST'])
def tymheredd_post():
    if not has_valid_api_key(request):
        app.logger.warning("Invalid or missing API key")
        return "Invalid or missing API key", 401

    if request.is_json:
        # TODO: put stuff in db
        data = request.json
        print("data is of type", type(data))
        print("data", data)
        if (("amser" in data)
            and ("tymheredd" in data)
            and ("gwasgedd" in data)
            and ("golau_light" in data)
            and ("golau_lux" in data)):
            data_dict = {
                "amser": data["amser"],
                "tymheredd": data["tymheredd"],
                "gwasgedd": data["gwasgedd"],
                "golau_light": data["golau_light"],
                "golau_lux": data["golau_lux"]
            }
            with pgdb.get_cursor() as cur:
                cur.execute("INSERT INTO darlleniad(amser, tymheredd, gwasgedd, golau_light, golau_lux) VALUES(%s, %s, %s, %s, %s)",
                            (data_dict["amser"], data_dict["tymheredd"], data_dict["gwasgedd"], data_dict["golau_light"], data_dict["golau_lux"]))

            return data_dict
    return "Bad request", 400

if __name__ == '__main__':
    app.run(host="10.0.1.201", port=5000, debug=True)

