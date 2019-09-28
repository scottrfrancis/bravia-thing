# Lambda to allow the Denon Thing's Mute status to control the Bravia-Thing's LED
#
# triggered by new document in a thing's ../shadow/update/document topic
#
# compares 'current' to 'previous' -- using shadow for state preservation
# if the 'Mute' property has changed, formats a 'LED' 'on' or 'off'
# request for the 'Bravia' thing
#

import sys
import logging
import json
import greengrasssdk



logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

client = greengrasssdk.client('iot-data')

def reportedToDesired_handler(event, context):
   logger.info("recevied " + json.dumps(event))
    try:
        reported = event['current']['state']['reported']
        mute = reported['Mute']
        vol = reported['Volume']

        # transform the desired state
        client.update_thing_shadow(thingName='Bravia',
            payload=json.dumps({"state":{"desired":{
                "Mute": mute.lower(),
                "Volume": vol
            }}}))
    except:
        pass

    return True
