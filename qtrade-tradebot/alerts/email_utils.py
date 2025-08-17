import os
import base64

from email.message import EmailMessage
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from .alerts import BaseAlert


# constants
from utils.env_vars import PATH_TO_TOKEN, PATH_TO_CRED, BOT_EMAIL
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


# EmailAlert to handle bot alerts sent with email
class EmailAlert(BaseAlert):
    def __init__(self) -> None:
        self.creds = self._get_creds()
        self.service = build('gmail', 'v1', credentials = self.creds)


    def _get_creds(self):
        # retrieve credentials and return a Credentials instance from API
        creds = None

        if PATH_TO_TOKEN and os.path.exists(PATH_TO_TOKEN):
            creds = Credentials.from_authorized_user_file(PATH_TO_TOKEN)
        
        if not creds or not creds.valid:
            # creds was not found or creds invalid, use credentials to validate
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError as err:
                    print("Token refresh failed: {err}")
                    creds = None
            
            if not creds:
                # PATH_TO_CRED must be defined: credentials are required and cannot be produced at runtime
                if not PATH_TO_CRED:
                    raise RuntimeError("Credential Path Undefined")
                
                flow = InstalledAppFlow.from_client_secrets_file(PATH_TO_CRED, SCOPES)
                creds = flow.run_local_server()

                if PATH_TO_TOKEN:
                    # cache token to file
                    with open(PATH_TO_TOKEN, 'w') as f:
                        f.write(creds.to_json())
                else:
                    raise RuntimeError("Token Path Undefined")
                
        # TODO: store token creds in db using token_manager
        return creds


    def send_msg(self, msg:str, recipient:str, subject:str):
        mail = EmailMessage()

        # set headers
        mail['To'] = recipient
        mail['From'] = BOT_EMAIL # always unchanged
        mail['Subject'] = subject
        

        # set content
        mail.set_content(msg)

        # no attachments expected so we will not use multipart MIME messages
        # TODO: consider adding some visuals to notification email

        # encode msg to url safe format then decode to python string
        encoded_mail = base64.urlsafe_b64encode(mail.as_bytes()).decode()
        
        create_mail = {"raw": encoded_mail}

        # send mail using service
        try:
            sent_message = (
                self.service.users()
                .messages()
                .send(userId = "me", body = create_mail)
                .execute()
            )
            return sent_message
        except HttpError as err:
            print(f"Error Occurred: {err}")
            return None

        # return sent_message

