"""Slack and email notification helpers."""
from __future__ import annotations

import json
import smtplib
from email.message import EmailMessage
from typing import Callable
from urllib.request import Request, urlopen


def send_slack(webhook_url: str, payload: dict, opener: Callable = urlopen) -> None:
    data = json.dumps(payload).encode("utf-8")
    request = Request(webhook_url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    opener(request, timeout=10)


def send_email(smtp_host: str, smtp_port: int, sender: str, recipients: list[str], subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content(body)
    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.send_message(message)
