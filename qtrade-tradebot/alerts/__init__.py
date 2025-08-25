from alerts.email_utils import EmailAlert
from alerts.push_utils import NTFYAlert
from alerts.base import BaseAlert

alert_channels: dict[str, type[BaseAlert]] = {
    "email": EmailAlert,
    "push": NTFYAlert,
}
    

def get_alert_channel(channel:str) -> BaseAlert:
    # call with desired channel to obtain the associated alerter
    try:
        # get type from alert_channels then init
        return alert_channels[channel]()
    except KeyError:
        raise RuntimeError("Invalid channel: {channel}")
