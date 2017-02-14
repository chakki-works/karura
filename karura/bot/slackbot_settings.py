import karura.env as env


API_TOKEN=env.get_slack_token()


PLUGINS = [
    "slackbot.plugins",
    "karura.bot.plugins",
]
