'''
Objective:
Create a class to handle all forms of alerts with a simple interface

Methods:
send_msgs()
'''
from dataclasses import dataclass
from typing import Optional

from alerts import get_alert_channel
from alerts import EmailAlert, DiscordAlert, NTFYAlert


@dataclass
class AlertConfig:
    # Email
    email_provider: Optional[str] = None
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_host: Optional[str] = None
    email_port: int = 587

    # Ntfy
    ntfy_topic: Optional[str] = None
    ntfy_auth_token: Optional[str] = None

    # Discord
    discord_webhook_url: Optional[str] = None

class Alerts:
    def __init__(self) -> None:
        self.email: EmailAlert = get_alert_channel('email')
        self.discord: DiscordAlert = get_alert_channel('discord')
        self.push: NTFYAlert = get_alert_channel('push')

    def send_msg(self):
        pass

    def set_configs(self, config: AlertConfig):
        pass
