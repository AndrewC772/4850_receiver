import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
import uuid
import datetime
import json
from pykafka import KafkaClient
import time
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

# with open('log_conf.yml', 'r') as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)


# logger = logging.getLogger('basicLogger')
# fh = logging.FileHandler('app.log')
# fh.setLevel(logging.DEBUG)
# logger.addHandler(fh)

current_kafka_retries = 0
max_kafka_retries = app_config["kafka"]["retry"]
while current_kafka_retries < max_kafka_retries:
    try:
        client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        producer = topic.get_sync_producer()
        break
    except:
        logger.error(f"Failed to connect to Kafka. Retrying in 5 seconds ")
        time.sleep(app_config["kafka"]["retry_wait"])
    current_kafka_retries += 1

def get_health():
    return 200

def post_device(body):
    trace_id = str(uuid.uuid4())
    body['trace_id'] = trace_id

    event_log_received = f"Received event post_device request with a trace id of {trace_id}"
    logging.info(event_log_received)

    msg = {"type": "device",
           "datetime":
               datetime.datetime.now().strftime(
                   "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    event_log_responded = f"Returned event post_device response (Id: {trace_id}) with status 201"
    logging.info(event_log_responded)
    
    return NoContent, 201


def post_network(body):
    trace_id = str(uuid.uuid4())
    body['trace_id'] = trace_id

    event_log_received = f"Received event post_network request with a trace id of {trace_id}"
    logging.info(event_log_received)

    msg = {"type": "network",
           "datetime":
               datetime.datetime.now().strftime(
                   "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    event_log_responded = f"Returned event post_network response (Id: {trace_id}) with status 201"
    logging.info(event_log_responded)

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')

app.add_api("openapi.yml",
            base_path="/receiver",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    # app.debug = True
    app.run(port=8080)
