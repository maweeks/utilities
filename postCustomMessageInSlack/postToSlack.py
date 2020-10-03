import json
import requests
import sys


def print_parameters():
    print("Parameters:")
    print("SLACK_TOKEN:   {0}".format(SLACK_TOKEN))
    print("SLACK_CHANNEL: {0}".format(SLACK_CHANNEL))
    print("SLACK_MESSAGE: {0}".format(SLACK_MESSAGE))


def generateMessageData():
    return {
        "channel": SLACK_CHANNEL,
        "text": "<!here> {0}".format(SLACK_MESSAGE)
    }


def postSlackMessage(data):
    try:
        postMessage = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": 'Bearer {0}'.format(SLACK_TOKEN),
                "Content-Type": "application/json"
            },
            data=json.dumps(data),
        )
        print(postMessage.json())
    except Exception:
        print("Failed to create release")
        raise SystemExit()


def runScript():
    postSlackMessage(generateMessageData())
    print("Script complete.")


# ######################################################################


SLACK_TOKEN = str(sys.argv[1])
SLACK_CHANNEL = str(sys.argv[2])
SLACK_MESSAGE = str(sys.argv[3])

if __name__ == '__main__':
    runScript()
