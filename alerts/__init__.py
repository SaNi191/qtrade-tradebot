from alerts.email_utils import EmailAlert
from alerts.push_utils import NTFYAlert
from alerts.discord_utils import DiscordAlert
from alerts.base import BaseAlert

# TODO: rework using alerts.handler 
# to provide a common interface for all alert types




alert_channels = {
    "email": EmailAlert,
    "push": NTFYAlert,
    'discord': DiscordAlert
}

def get_alert_channel(channel:str):
    # call with desired channel to obtain the associated alerter
    try:
        # get type from alert_channels then init
        return alert_channels[channel]()
    except KeyError:
        raise RuntimeError("Invalid channel: {channel}")
