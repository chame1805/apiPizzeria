import json
import os
from pathlib import Path
from typing import Any

import firebase_admin
from firebase_admin import credentials, messaging


def _get_credentials_file_path() -> Path:
    value = os.getenv("FIREBASE_CREDENTIALS_FILE", "firebase-service-account.json")
    return Path(value).expanduser().resolve()


def init_firebase_if_configured() -> bool:
    if firebase_admin._apps:
        return True

    project_id = os.getenv("FIREBASE_PROJECT_ID")
    credentials_path = _get_credentials_file_path()
    if not project_id or not credentials_path.exists():
        return False

    with credentials_path.open("r", encoding="utf-8") as fh:
        raw: dict[str, Any] = json.load(fh)

    cred = credentials.Certificate(raw)
    firebase_admin.initialize_app(cred, {"projectId": project_id})
    return True


def send_push_to_token(token: str, title: str, body: str, data: dict[str, str]) -> None:
    message = messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body),
        data=data,
        android=messaging.AndroidConfig(priority="high"),
    )
    messaging.send(message)
