import json

from utils.Lambdas_Helpers import slack_message
from utils.Misc import Misc
from utils.aws.Lambdas import Lambdas


def run(event, context):
    team_id = 'T7F3AUXGV'
    channel = 'DDKUZTK6X'
    querystring = event.get('queryStringParameters')
    if querystring and querystring.get('file_id'):
        file_id = querystring.get('file_id')
        payload  = {"params": [ "sync_sheet",file_id], "channel": "DDKUZTK6X", 'team_id': 'T7F3AUXGV'}
        Lambdas('gs.elastic_jira').invoke(payload)
        text = "[trigger_sync_jira_sheets] completed workflow for file_id: {0} , see channel {1} for more details".format(file_id,channel)
        status_code = 201
    else:
        text ="Error: file_id value not provided"
        status_code = 501

    slack_message(text, [], channel,team_id)


    return {
                'headers'        : {'Content-Type': 'application/json'},
                "statusCode"     : status_code,
                "body"           : Misc.json_format({'text': text})
            }