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

    # Discord
    discord_webhook_url: Optional[str] = None

    @property
    def email_valid(self):
        return all([
            self.email_provider, 
            self.email_username, 
            self.email_password,
            self.email_host,
            self.email_port
        ])
    
    @property
    def nfty_valid(self):
        return self.ntfy_topic is not None
    
    @property
    def discord_valid(self):
        return self.discord_webhook_url is not None
    
    
class Alerts:
    def __init__(self) -> None:
        self.email: EmailAlert = get_alert_channel('email')
        self.discord: DiscordAlert = get_alert_channel('discord')
        self.push: NTFYAlert = get_alert_channel('push')

    def send_msg(self, msg, recipient, subject):
        '''
        message sending handler: assumes that configs have been set
        configures and sends message for each valid channel
        '''
        assert(self.config is not None)
        cfg = self.config

        if cfg.discord_valid:
            self.discord.configure(cfg.discord_webhook_url)
            self.discord.send_msg(msg, recipient, subject)
        
        if cfg.email_valid:
            self.email.configure(
                cfg.email_username, 
                cfg.email_password, 
                cfg.email_host, 
                cfg.email_port
            )

            self.email.send_msg(msg, recipient, subject)
        
        if cfg.nfty_valid:
            self.push.configure(cfg.ntfy_topic)
            self.email.send_msg(msg, recipient, subject)

    def set_config(self, config: AlertConfig):
        '''
        users of module should get AlertConfig dataclass and set desired values
        then send config to set_config to configure channels
        '''
        self.config = config

