#!/usr/bin/python3

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import Shadow

import argparse
from datetime import datetime
import json
import logging
from os.path import abspath
import time

import BraviaQuery


# Read in command-line parameters
parser = argparse.ArgumentParser()
# IOT args
parser.add_argument("-e", "--endpoint", action="store", required=True,
                    dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store",
                    required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store",
                    dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store",
                    dest="privateKeyPath", help="Private key file path")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-n", "--thingName", action="store",
                    dest="thingName", required=True, help="Targeted thing name")
parser.add_argument("-id", "--clientId", action="store",
                    dest="clientId", help="Targeted client id")
parser.add_argument("-t", "--timeout", action="store", dest="timeout",
                    default="0.5", help="Timeout to wait for events")

# ip address of TV
parser.add_argument("-ip", "--tvIP", action="store",
                    required=True, dest="tv_ip", help="IP address of TV")
parser.add_argument("--psk", "--braviaKey", action="store", required=True,
                    dest="psk", default="0000", help="Pre-Shared Key for Bravia")


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

timeout = float(args.timeout)

tv_ip = args.tv_ip
psk = args.psk

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error(
        "X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.WARN)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

connection = BraviaQuery.BraviaQuery(tv_ip, psk)


def customShadowCallback_Update(payload, responseStatus, token):
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")

    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

def customShadowCallback_Delta(payload, responseStatus, token):
    logger.warn("Received a delta message:")
    payloadDict = json.loads(payload)
    deltaMessage = json.dumps(payloadDict["state"])
    logger.warn(deltaMessage + "\n")

    muteOn = False
    if 'Mute' in payloadDict['state']:
        muteOn = payloadDict['state']['Mute'].lower() == "on"
        connection.setMute(payloadDict['state']['Mute'])

    if 'Volume' in payloadDict['state'] and not muteOn:
        connection.setVolume(int(payloadDict['state']['Volume']))


mqtttc = AWSIoTMQTTShadowClient(thingName)
mqtttc.configureEndpoint(host, 8883)
mqtttc.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTShadowClient configuration
mqtttc.configureAutoReconnectBackoffTime(1, 32, 20)
mqtttc.configureConnectDisconnectTimeout(10)  # 10 sec
mqtttc.configureMQTTOperationTimeout(5)  # 5 sec

# Connect to AWS IoT
mqtttc.connect()

# Create a deviceShadow with persistent subscription
deviceShadowHandler = mqtttc.createShadowHandlerWithName(thingName, True)

# Listen on deltas
deviceShadowHandler.shadowRegisterDeltaCallback(customShadowCallback_Delta)

last_power = ''


def do_something():
    global last_power
    try:
        state = connection.poll()
        if state['Power'] != last_power:
            logger.warn('Power state changed, sending ' + json.dumps(state))
            # not really a warning, but INFO & Debug is too noisy
            last_power = state['Power']
    
            # mqtttc.publish(topicName, json.dumps(state), 0)
            deviceShadowHandler.shadowUpdate(Shadow.makeStatePayload(
                "reported", state), customShadowCallback_Update, 5)

    except Exception as e:
        logger.info(e)
        pass


def run():
    while True:
        time.sleep(0.9*timeout)         # crude approach to timing adjustment
        do_something()


if __name__ == "__main__":
    run()
