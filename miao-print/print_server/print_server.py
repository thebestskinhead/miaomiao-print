# -*- coding: utf-8 -*-cd

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from message_process import BtManager
import base64
import cv2
import numpy as np
from image_process import ImageConverter, TextConverter
from functools import wraps

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
mmj = None

def check_connection(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        global mmj
        if not mmj or not mmj.connected:
            return jsonify({"success": False, "error": "打印机未连接"})
        return f(*args, **kwargs)
    return wrapped

@app.route('/status', methods=['GET'])
def get_status():
    global mmj
    if mmj and mmj.connected:
        return jsonify({"connected": True})
    else:
        return jsonify({"connected": False})

@app.route('/connect', methods=['POST'])
def connect_printer():
    global mmj
    mac_address = request.json.get('macAddress')
    try:
        if mac_address:
            mmj = BtManager(mac_address)
        else:
            mmj = BtManager()
        if mmj.connected:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "无法连接打印机"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/print', methods=['POST'])
@check_connection
def print_content():
    global mmj
    text = request.json.get('text')
    image_data = request.json.get('image')

    try:
        if text:
            if isinstance(text, unicode):
                text = text.encode('utf-8')
            img = TextConverter.text2bmp(text)
            mmj.sendImageToBt(img)
        if image_data:
            if isinstance(image_data, unicode):
                image_data = image_data.encode('utf-8')
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img = ImageConverter.image2bmp(img)
            mmj.sendImageToBt(img)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)