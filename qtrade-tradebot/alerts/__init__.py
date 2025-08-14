from .email_utils import EmailAlert
from .sms_utils import SMSAlert
from alerts import BaseAlert

alert_channels: dict[str, type[BaseAlert]] = {
    "email": EmailAlert,
    "sms": SMSAlert,
}
    

def get_alert_channel(channel:str) -> BaseAlert:
    # call with desired channel to obtain the associated alerter
    try:
        # get type from alert_channels then init
        return alert_channels[channel]()
    except KeyError:
        raise RuntimeError("Invalid channel: {channel}")
