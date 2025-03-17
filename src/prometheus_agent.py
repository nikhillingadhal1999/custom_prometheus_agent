from prometheus_client import Gauge, start_http_server
import psutil 
import time
import sys
import os

root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,root_path)
from config.configuration import CA_PATH , CERT_PATH, KEY_PATH
from logging_module.logger import get_logger
from file_recognition.exec_file import execute
logger = get_logger(__name__)

logger.info("prometheus is running") 

def convert_to_data_type(value):
    if isinstance(value, str) and '%' in value:
        return float(value.strip('%'))
    elif isinstance(value, str) and ('GB' in value or 'MB' in value):
        return float(value.split()[0].replace(',', ''))
    return value
gauges = []

def measure(init_flag):
    exec_result = execute()
    print(exec_result)
    global gauges
    count = 0
    for data in exec_result:
        results= data['result']
        labels = data['labels']
        gauge_name = '_'.join(labels).lower() + "_gauge"
        print(labels)
        if init_flag:
            gauge = Gauge(gauge_name, f"{gauge_name} for different metrics", labels)
            gauges.append(gauge)
        else:
            gauge = gauges[count]
            count += 1
        for result in results:
            print(result,isinstance(result['label'],list))
            if isinstance(result['label'],str):
                gauge.labels(result['label']).set(convert_to_data_type(result['value']))
            elif isinstance(result['label'],list):
                label_dict = dict(zip(labels, result['label']))
                gauge.labels(**label_dict).set(convert_to_data_type(result['value']))

print("Starting server")

start_http_server(8000)
flag = True
while True:
    measure(flag)
    flag = False
    time.sleep(5)
