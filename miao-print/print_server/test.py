# -*- coding: utf-8 -*-
from __future__ import print_function
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import traceback
import base64
import cv2
import numpy as np
from StringIO import StringIO
import re
import threading
from functools import wraps

# 假设这些自定义模块已适配Python 2
from message_process import BtManager
from image_process import ImageConverter, TextConverter

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# 线程安全全局变量
bt_lock = threading.Lock()
mmj = None

# MAC地址验证正则
MAC_REGEX = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')

def check_connection(f):
    """连接状态检查装饰器"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        global mmj
        with bt_lock:
            if not mmj or not getattr(mmj, 'connected', False):
                return jsonify({"success": False, "error": u"打印机未连接"}), 400
        return f(*args, **kwargs)
    return wrapped

def validate_image(data):
    """图像数据基础验证"""
    if not data:
        return False
    try:
        if len(data) % 4 != 0:
            return False
        return base64.b64decode(data[:64]) is not None
    except:
        return False

@app.route('/status', methods=['GET'])
def get_status():
    with bt_lock:
        status = bool(mmj and getattr(mmj, 'connected', False))
    return jsonify({"connected": status})

@app.route('/connect', methods=['POST'])
def connect_printer():
    global mmj
    if not request.is_json:
        return jsonify({"success": False, "error": u"请求必须为JSON格式"}), 400

    data = request.get_json()
    mac_address = data.get('macAddress', '').strip() if data else None

    # MAC地址格式验证
    if mac_address and not MAC_REGEX.match(mac_address):
        return jsonify({"success": False, "error": u"无效的MAC地址格式"}), 400

    try:
        with bt_lock:
            # 清理现有连接
            if mmj and getattr(mmj, 'connected', False):
                mmj.close()

            # 创建新连接
            mmj = BtManager(mac_address) if mac_address else BtManager()
            
            if not getattr(mmj, 'connected', False):
                raise RuntimeError(u"连接失败，请检查打印机状态")

            return jsonify({"success": True})

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
        return jsonify({
            "success": False,
            "error": u"连接错误: {}".format(str(e).decode('utf-8', 'replace') if isinstance(e, str) else unicode(e))
        }), 500
    finally:
        with bt_lock:
            if mmj and not getattr(mmj, 'connected', False):
                mmj = None

@app.route('/print', methods=['POST'])
@check_connection
def print_content():
    global mmj
    data = request.get_json()

    text = data.get('text', '') if data else None
    image_data = data.get('image', '') if data else None

    try:
        with bt_lock:
            # 文本处理
            if text:
                if isinstance(text, unicode):
                    text = text.encode('utf-8')
                img_buffer = TextConverter.text2bmp(text)
                mmj.sendImageToBt(img_buffer.getvalue())

            # 图像处理
            if image_data:
                if isinstance(image_data, unicode):
                    image_data = image_data.encode('utf-8')
                
                if not validate_image(image_data):
                    raise ValueError(u"无效的图像数据")

                img_bytes = base64.b64decode(image_data)
                nparr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is None:
                    raise ValueError(u"图像解码失败")
                
                img_buffer = ImageConverter.image2bmp(img)
                mmj.sendImageToBt(img_buffer.getvalue())

            return jsonify({"success": True})

    except Exception as e:
        exc_info = sys.exc_info()
        app.logger.error(u"打印错误: %s", traceback.format_exception(*exc_info))
        return jsonify({
            "success": False,
            "error": u"打印失败: {}".format(unicode(e).encode('utf-8', 'replace') if isinstance(e, Exception) else str(e))
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
