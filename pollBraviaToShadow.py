#!/usr/bin/python3

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import Shadow

import argparse
from datetime import datetime
import json
import logging
from os.path import abspath
import time

# import BraviaProtocol
import BraviaQuery


# Read in command-line parameters
parser = argparse.ArgumentParser()
# IOT args
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-n", "--thingName", action="store", dest="thingName", required=True, help="Targeted thing name")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", help="Targeted client id")
parser.add_argument("-t", "--timeout", action="store", dest="timeout", default="0.5", help="Timeout to wait for events")
parser.add_argument('-p', "--topic", action="store", dest="topicName", required=True, help="Topic to pubilsh on")

# ip address of TV
parser.add_argument("-ip", "--tvIP", action="store", required=True, dest="tv_ip", help="IP address of TV")
parser.add_argument("--psk", "--braviaKey", action="store", required=True, dest="psk", default="0000", help="Pre-Shared Key for Bravia")


args = parser.parse_args()
host = args.host
rootCAPath = abspath(args.rootCAPath)
certificatePath = abspath(args.certificatePath)
privateKeyPath = abspath(args.privateKeyPath)
useWebsocket = args.useWebsocket
thingName = args.thingName
clientId = args.clientId
if (clientId == None):
    clientId = thingName
topicName = args.topicName

timeout = float(args.timeout)

tv_ip = args.tv_ip
psk = args.psk

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

connection = BraviaQuery.BraviaQuery(tv_ip, psk)
# protocol = BraviaProtocol.BraviaProtocol()

mqtttc = AWSIoTMQTTClient(thingName)
mqtttc.configureEndpoint(host, 8883)
mqtttc.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

mqtttc.connect()


def do_something():
    state = connection.poll()
    try:
        mqtttc.publish(topicName, json.dumps(state), 0)

    except Exception as e:
        logger.info(e)
        pass


def run():
    while True:
        time.sleep(0.9*timeout)         # crude approach to timing adjustment
        do_something()
        

if __name__ == "__main__":
    run()
