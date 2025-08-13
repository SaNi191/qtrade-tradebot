# TODO: add SMSALert functionality

from .alerts import BaseAlert

class SMSAlert(BaseAlert):
    def send_msg(self, msg:str,  recipient:str, subject:str):
        pass

