import email
import google.auth


from googleapiclient.discovery import build


from .alerts import BaseAlert

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class EmailAlert(BaseAlert):
    def __init__(self) -> None:
        creds = self.get_creds()
        service = build('gmail', 'v1', credentials = creds)

    def get_creds(self):
        pass

    def send_msg(self, msg:str,  recipient:str, subject:str):
        pass
    pass