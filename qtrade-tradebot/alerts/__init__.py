from .email_utils import EmailAlert
from .sms_utils import SMSAlert

def get_alert_channel(channel:str):
    # call with desired channel to obtain the associated alerter
    if channel.lower() == "email":
        return EmailAlert()
    elif channel.lower() == "sms":
        return SMSAlert()
    else:
        print("not yet implemented")
    
    return RuntimeError("Invalid channel")