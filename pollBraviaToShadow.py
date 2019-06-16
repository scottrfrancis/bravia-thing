#!/usr/bin/python3

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import Shadow

import argparse
from datetime import datetime
import json
import logging
import time

import BraviaProtocol
import BraviaQuery


# remote debug harness 
# import ptvsd
# import socket
# this_ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
# ptvsd.enable_attach(address=(this_ip,3000), redirect_output=True)
# ptvsd.wait_for_attach()
# end debug harness


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
parser.add_argument("-id", "--clientId", action="store", dest="clientId", required=True, help="Targeted client id")

parser.add_argument("-t", "--timeout", action="store", required=True, dest="timeout", default="0.5", help="Timeout to wait for events")

# ip address of TV
parser.add_argument("-ip", "--tvIP", action="store", required=True, dest="tv_ip", help="IP address of TV")
parser.add_argument("--psk", "--bravieKey", action="store", required=True, dest="psk", default="0000", help="Pre-Shared Key for Bravia")


args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
useWebsocket = args.useWebsocket
thingName = args.thingName
clientId = args.clientId

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
protocol = BraviaProtocol.BraviaProtocol()


# Custom Shadow callback
def customShadowCallback_Update(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")
    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("payload: " + json.dumps(payloadDict)) #["state"]["desired"]["property"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

class shadowCallbackContainer:
    def __init__(self, deviceShadowInstance):
        self.deviceShadowInstance = deviceShadowInstance

    # Custom Shadow callback
    def customShadowCallback_Delta(self, payload, responseStatus, token):
        print("\nERROR!!! we should never receive a delta message\n")

        print("Received a delta message:")
        payloadDict = json.loads(payload)
        deltaMessage = json.dumps(payloadDict["state"])
        print(deltaMessage + "\n")

        commands = protocol.makeCommands(payloadDict["state"])
        print("\nbuilt commands: " + str(commands) + "\n")
        connection.send(commands)


# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None
if useWebsocket:
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId, useWebsocket=True)
    myAWSIoTMQTTShadowClient.configureEndpoint(host, 443)
    myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId)
    myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTShadowClient configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

# Create a deviceShadow with persistent subscription
deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(thingName, True)

shadowCallbackContainer_Bot = shadowCallbackContainer(deviceShadowHandler)

protocol = BraviaProtocol()

def do_something():
    events = connection.poll()

    if protocol.parseEvents(events):
        print( "\n\nEvents: " + str(events) + "\n\n" )
        state = protocol.getState()
        # print str(datetime.now()) + " - " + json.dumps(state)
        deviceShadowHandler.shadowUpdate(Shadow.makeStatePayload("reported", state), customShadowCallback_Update, 5)


def run():
    while True:
        time.sleep(0.9*timeout)         # crude approach to timing adjustment
        do_something()

if __name__ == "__main__":
    run()
