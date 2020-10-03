import json
import requests
import sys


SLACK_TOKEN = str(sys.argv[1])
SLACK_CHANNEL = str(sys.argv[2])
SLACK_MESSAGE = str(sys.argv[3])


# ######################################################################


def print_parameters():
    print("Parameters:")
    print("SLACK_TOKEN:   {0}".format(SLACK_TOKEN))
    print("SLACK_CHANNEL: {0}".format(SLACK_CHANNEL))
    print("SLACK_MESSAGE: {0}".format(SLACK_MESSAGE))


def generate_message_data(message):
    return {
        "channel": SLACK_CHANNEL,
        "text": message
    }


def post_slack_message(data):
    try:
        post_message = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": 'Bearer {0}'.format(SLACK_TOKEN),
                "Content-Type": "application/json"
            },
            data=json.dumps(data),
        )
        print(post_message.json())
    except Exception:
        print("Failed to send slack message")
        raise SystemExit()


def run_script():
    data = generate_message_data("<!here> {0}".format(SLACK_MESSAGE))
    post_slack_message(data)
    print("Script complete.")


# ######################################################################


if __name__ == '__main__':
    run_script()
