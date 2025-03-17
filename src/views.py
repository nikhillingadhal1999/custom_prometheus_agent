import sys
import os
root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,root_path)
from flask import Flask, jsonify
from logging_module.logger import get_logger
from config.configuration import CA_PATH, CERT_PATH , KEY_PATH

logger = get_logger(__name__)
app = Flask(__name__)


@app.route('/health',methods=['GET'])
def health():
    return jsonify({"status":"healthy"}), 200

def start_flask():
    logger.info("Application started successfully")
    context = (CERT_PATH,KEY_PATH)
    app.run(host="0.0.0.0", port=8000, ssl_context=context)
if __name__ == "__main__":
        start_flask()
