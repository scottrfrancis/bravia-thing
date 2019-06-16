import json

# class Shadow:
#     @staticmethod
#     
def makeStatePayload(type, parameters):
    payload = {'state': {type: parameters}}
    return json.dumps(payload)
