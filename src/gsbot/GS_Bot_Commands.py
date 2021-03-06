from datetime import datetime

from utils.Lambdas_Helpers       import slack_message
from utils.aws.Lambdas           import Lambdas


class GS_Bot_Commands:                                      # move to separate class
    @staticmethod
    def hello(slack_event, params=None):
        user = slack_event.get('user')
        return 'Hello <@{0}>, how can I help you?'.format(user), []

    @staticmethod
    def help(slack_event, params=None):
        commands        = [func for func in dir(GS_Bot_Commands) if callable(getattr(GS_Bot_Commands, func)) and not func.startswith("__")]
        title           = "*Here are the commands available*"
        attachment_text = ""
        for command in commands:
            if command is not 'bad_cmd':
                attachment_text += " • {0}\n".format(command)
        return title,[{'text': attachment_text, 'color': 'good'}]


    @staticmethod
    def bad_cmd(slack_event, params=None):
        (text, attachments) = GS_Bot_Commands.help(slack_event['text'])
        text = ':exclamation: Sorry, could not match provided command to a method: `{0}`\n'.format(slack_event['text']) + text
        return (text, attachments)

    # refactor into separate class
    @staticmethod
    def dot_render(slack_event, params=None):

        text       = slack_event["text"]
        channel_id = slack_event["channel"]
        code = text.split("```")
        if len(code) != 3:
            text = '*GS Bot command execution error :exclamation:*'
            attachments = [{ "text": 'you need to provide the code to red inside *```* blocks', 'color': 'danger'}]
            return text, attachments

        dot = "digraph G {\n" + code[1] + "\n }"

        text        = ":information_source:  Rending dot code with size: {0}".format(len(dot))
        attachments = []

        Lambdas('utils.dot_to_slack').invoke_async({'dot': dot , 'channel' : channel_id})
        return text, attachments


    # refactor into separate class
    @staticmethod
    def plantuml(slack_event, params=None):
        text    = slack_event["text"]
        channel = slack_event["channel"]
        code    = text.split("```")
        if len(code) != 3:
            text = '*GS Bot command execution error :exclamation:*'
            attachments = [{"text": 'you need to provide the code to red inside *```* blocks', 'color': 'danger'}]
            return text, attachments
        puml = "@startuml \n" + code[1] + "\n@enduml"

        text        = ":information_source:  Rending puml code with size: {0}".format(len(puml))
        attachments = [{"text": '```{0}```'.format(puml), 'color': 'good'}]

        Lambdas('utils.puml_to_slack').invoke_async({'puml': puml, 'channel': channel})
        return text, attachments

    #move to new routing mode
    @staticmethod
    def browser(slack_event, params=None):
        Lambdas('browser.lambda_browser').invoke_async({'params': params, 'data': slack_event})
        return None, None

    # move to new routing mode
    @staticmethod
    def gdocs(slack_event, params=None):
        Lambdas('gs.lambda_gdocs'       ).invoke_async({'params': params, 'data': slack_event})

        return None, None

    @staticmethod
    def mindmap(slack_event, params=None):
        channel = slack_event.get('channel')
        team_id = slack_event.get('team_id')
        if len(params) < 1:
            text = ':red_circle: Hi, for the `mindmap` command, you need to provide an `graph_name`'
            slack_message(text, [], channel, team_id)
            return None, None
        graph_name = params.pop(0)
        graph_params = ['go_js', graph_name, 'mindmap']
        graph_params.extend(params)
        Lambdas('browser.lambda_browser').invoke_async({"params": graph_params, 'data': {'team_id': team_id, 'channel': channel}})
        return None, None
    
    # @staticmethod
    # def graph(slack_event, params=[]):
    #     return Lambdas('gs.lambda_graph'       ).invoke({'params': params, 'data': slack_event}) , []
    #     return None, None

    # move to new routing mode
    @staticmethod
    def slides(slack_event, params=None):
        Lambdas('gs.lambda_slides'      ).invoke_async({'params': params, 'data': slack_event})
        return (None, None)

    # move to new routing mode
    @staticmethod
    def sheets(slack_event, params=[]):
        Lambdas('gs.lambda_sheets').invoke_async({'params': params, 'data': slack_event})
        return (None, None)

    # move to new routing mode
    @staticmethod
    def jira(slack_event, params=[]):
        Lambdas('gs.elastic_jira').invoke_async({"params": params , "user": slack_event.get('user') , "channel": slack_event.get('channel'), 'team_id': slack_event.get('team_id') },)
        return None, None

    @staticmethod
    def time(slack_event, params=[]):
        user = slack_event.get('user')
        return 'Hi <@{0}>, the time now is: {1}'.format(user, datetime.now()), []

    @staticmethod
    def version(slack_event, params=[]):
        return 'The current version of GSBot is v0.5',None

    # @staticmethod
    # def reload_jira_lambda(slack_event=None, params=None):
    #     Lambdas('gs.elastic_jira').update_with_src()
    #     return "::white_check_mark: gs.elastic_jira lambda has been reloaded"



