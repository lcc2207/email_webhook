#!/usr/bin/env python
import binascii
import hmac
import json
import logging
import os
import time
import smtplib
from datetime import datetime
from hashlib import sha1

import dateutil.parser
import pytz
import requests
from flask import Flask, abort, jsonify, request
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# Configuration variables
SCALR_SIGNING_KEY = os.getenv('SCALR_SIGNING_KEY', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', '')
SMTP_FROM = os.getenv('SMTP_FROM', '')
SMTP_PORT = os.getenv('SMTP_PORT', 25)
SMTP_TO = os.getenv('SMTP_TO', '')
BACKEND_VERIFY = os.getenv('BACKEND_VERIFY', 'true').lower() == 'true'
# The maximum time allowed between the moment a request is signed and the moment the signature stops
# being valid (in seconds)
MAX_AGE_SIGNATURE = 300

# Print configuration
logging.info("> Configuration variables")
for var in ['SCALR_SIGNING_KEY', 'SMTP_SERVER', 'BACKEND_VERIFY']:
    logging.info('Config: %s = %s', var, globals()[var] if 'PASS' not in var else '*' * len(globals()[var]))


@app.route("/sendmail/", methods=['POST'])
def webhook_listener():
    """ Handle webhook requests sent by Scalr. """
    logging.debug("Received request with payload = %s", request.data)

    if not validate_request(request):
        abort(403)

    try:
        data = json.loads(request.data)
    except ValueError:
        logging.warn("Invalid JSON payload")
        abort(400)

    if 'eventName' not in data or 'data' not in data or 'userData' not in data:
        logging.warn('Invalid request received')
        abort(400)

    if data['eventName'] == 'HostUp':
        return sendmail(
            smtp_server=SMTP_SERVER,
            smtp_from=SMTP_FROM,
            smtp_to=data['data'].get(SMTP_TO).split(),
            smtp_port=SMTP_PORT,
            host=data['data'].get('SCALR_SERVER_HOSTNAME'),
            data=data,
        )
    else:
        logging.warn('Received request for unhandled event %s', data['eventName'])
        return jsonify({'success': False})


def sendmail(smtp_server, smtp_from, smtp_to, smtp_port, host, data):
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(1)
        msg = "Hello!\n Host: " + host + " is complete"
        logging.warn(smtp_to)
        server.sendmail(smtp_from, smtp_to, msg)

    except ConnectionError as e:
        logging.error("Backend failure: %s", e)
        return jsonify({'success': False, 'msg': 'Cannot connect to backend: {}'.format(e)}), 500
    except ValueError as e:
        logging.error("Backend failure: %s", e)
        return jsonify({'success': False, 'msg': 'Invalid response from backend: {}'.format(e)}), 500
    except Exception as e:
        logging.error("Backend failure: %s", e)
        return jsonify({'success': False, 'msg': 'Backend failure: {}'.format(e)}), 500
    webhook_response = {
        'success': True,
    }
    logging.debug('email response: %s', data)
    logging.debug('Returning payload to scalr server: %s', webhook_response)
    return jsonify(webhook_response)


def validate_request(request):
    """ Validate webhook authenticity """
    if 'X-Signature' not in request.headers or 'Date' not in request.headers:
        logging.warn('Missing signature headers')
        return False

    # Compute our signature
    date = request.headers['Date']
    body = request.data
    expected_signature = binascii.hexlify(hmac.new(SCALR_SIGNING_KEY, body + date, sha1).digest())
    if expected_signature != request.headers['X-Signature']:
        logging.warn('Signature does not match')
        return False

    # Check for freshness (this still allows rapid replay attack)
    date = dateutil.parser.parse(date)
    now = datetime.now(pytz.utc)
    delta = abs((now - date).total_seconds())
    if delta >= MAX_AGE_SIGNATURE:
        logging.warn('Signature is too old (%ds)' % delta)
        return False

    return True


if __name__ == '__main__':
    logging.info("Starting development server...")
    app.run(debug=True, host='127.0.0.1')
