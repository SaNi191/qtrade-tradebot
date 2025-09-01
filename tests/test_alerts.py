# tests/test_alerts.py
import pytest
import logging
import os
import sys

from unittest.mock import patch, MagicMock

from alerts.handler import Alerts, AlertConfig
from alerts.email_utils import EmailAlert
from alerts.discord_utils import DiscordAlert
from alerts.push_utils import NTFYAlert



@pytest.fixture
def email_alert():
    return EmailAlert()

@pytest.fixture
def discord_alert():
    return DiscordAlert()

@pytest.fixture
def ntfy_alert():
    return NTFYAlert()


# -------------------------
# EmailAlert tests
# -------------------------
def test_email_send_success(email_alert):
    email_alert.configure("user@test.com", "password", "smtp.test.com", 587)

    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = email_alert.send_msg("hello", "to@test.com", "subject")

        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@test.com", "password")
        mock_server.send_message.assert_called_once()


def test_email_send_failure(email_alert, caplog):
    email_alert.configure("user@test.com", "password", "smtp.test.com", 587)

    with patch("smtplib.SMTP", side_effect=Exception("fail")):
        with caplog.at_level(logging.ERROR):
            result = email_alert.send_msg("hello", "to@test.com", "subject")

    assert result is False
    assert "Error Occurred" in caplog.text


def test_email_send_not_configured(email_alert, caplog):
    with caplog.at_level(logging.ERROR):
        result = email_alert.send_msg("hello", "to@test.com", "subject")

    assert result is False
    assert "not yet configured" in caplog.text


# -------------------------
# DiscordAlert tests
# -------------------------
def test_discord_send_success(discord_alert):
    discord_alert.configure("https://discord.test/webhook")

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 204
        result = discord_alert.send_msg("test msg")

    assert result is True
    mock_post.assert_called_once()


def test_discord_send_failure(discord_alert):
    discord_alert.configure("https://discord.test/webhook")

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 400
        result = discord_alert.send_msg("test msg")

    assert result is False


def test_discord_not_configured(discord_alert, caplog):
    with caplog.at_level(logging.ERROR):
        result = discord_alert.send_msg("msg")

    assert result is False
    assert "not yet configured" in caplog.text


# -------------------------
# NTFYAlert tests
# -------------------------
def test_ntfy_send_success(ntfy_alert):
    ntfy_alert.configure("mytopic")

    with patch("requests.post") as mock_post:
        mock_post.return_value.ok = True
        result = ntfy_alert.send_msg("hello", "recipient", "subject")

    assert result is True
    mock_post.assert_called_once()


def test_ntfy_send_failure(ntfy_alert):
    ntfy_alert.configure("mytopic")

    with patch("requests.post") as mock_post:
        mock_post.return_value.ok = False
        result = ntfy_alert.send_msg("hello", "recipient", "subject")

    assert result is False


def test_ntfy_not_configured(ntfy_alert, caplog):
    with caplog.at_level(logging.ERROR):
        result = ntfy_alert.send_msg("hello", "recipient", "subject")

    assert result is False
    assert "not yet configured" in caplog.text


# -------------------------
# Alerts integration
# -------------------------
def test_alerts_send_all_channels(monkeypatch):
    alerts = Alerts()
    cfg = AlertConfig(
        email_provider="gmail",
        email_username="user@test.com",
        email_password="pass",
        email_host="smtp.test.com",
        email_port=587,
        ntfy_topic="mytopic",
        discord_webhook_url="https://discord.test/webhook"
    )
    alerts.set_config(cfg)

    monkeypatch.setattr(alerts.email, "send_msg", lambda *a, **kw: True)
    monkeypatch.setattr(alerts.discord, "send_msg", lambda *a, **kw: True)
    monkeypatch.setattr(alerts.push, "send_msg", lambda *a, **kw: True)

    alerts.send_msg("msg", "to@test.com", "subject")
