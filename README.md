# Bravia-Thing

Polls a Television on the local network using the [Bravia REST API](https://pro-bravia.sony.net/develop/integrate/rest-api/spec/getting-started) and updates an AWS IoT Device Shadow with the status. 

## Objective

Wish to use the TV Power as a signal to drive further automation of other entertainment systems -- notably an AVR as described in this [blog post](https://scottrfrancis.wordpress.com/2017/12/10/adding-alexa-to-an-old-av-receiver).

## Environment

This script has been tested with a Sony XBR55X900E and XBR65X900E, but should generally work for any of the [Sony Bravia Products](https://pro.sony/ue_US/products/professional-displays).

## Design

Following my [Denon Thing](https://github.com/scottrfrancis/DenonPy) design, there is an outer *Python 3* program, `pollBraviaToShadow.py` that implements the AWS IoT Thing-ness. The `BraviaQuery.py` object relies on [appagara's](https://github.com/aparraga) excellent [braviarc](https://github.com/aparraga/braviarc) package. On a regular interval, the poll() method calls get_power_status() and sends the state to the Shadow.

The Shadow operations are one way as no Delta handling implementation has been given. This is consistent with wanting to use the TV power signal as a 'master trigger' for automation activities. A Shadow implmementation was chosen over a Telemetry implementation (as would normally be [recommended](https://d1.awsstatic.com/whitepapers/Designing_MQTT_Topics_for_AWS_IoT_Core.pdf)) to facilitate the shadow/document behavior. The `$aws/things/Bravia/shadow/update/document` topic publishes updated state documents that include *BOTH* current and previous state. Thus, state management is pushed to the Shadow Service and eases the implementation of triggered Lambdas and the device software.

An alternate Telemetry implementation is also provided, but hasn't been as thoroughly tested.

## Setup
*AWSIoTPythonSDK*
```
pip3 install AWSIoTPythonSDK
```

also using braviarc, which relies on requests, so install that with pip
```
pip3 install requests
```

*braviarc*
```
pip3 install git+https://github.com/aparraga/braviarc.git
```

## Usage

See `start.sh` for example invocation. Be sure to supply the appropriate endpoint, certificates, etc. Available options are near the top of `pollBraviaToShadow.py`. *NB*- If using Greengrass, supply IP and the right root-ca.

### TODOs
[ ] implement Greengrass Discovery to handle fail over and startup
[ ] wrap the connect with some retry logic for bootup race condition problems
