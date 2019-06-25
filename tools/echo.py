# Simple AWS Greengrass Lambda function to log a message received on a topic
# Make sure your subscription routes traffic from this Lambda to the  topic

import sys
import logging
import json
import greengrasssdk

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

client = greengrasssdk.client('iot-data')

def RatchetHello_handler(event, context):
    logger.info("Ratchet Lambda is ONLINE")
    logger.info(json.dumps(event))

    # Let's publish a response back to AWS IoT
    client.publish(topic = "/echo-cloud", payload = json.dumps(event))

    return True
