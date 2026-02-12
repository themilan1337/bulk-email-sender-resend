"""Persistent settings management using QSettings."""

from PyQt6.QtCore import QSettings


APP_NAME = "BulkEmailSender"
ORG_NAME = "ResendMailer"


class AppConfig:
    """Wrapper around QSettings for persistent key-value storage."""

    def __init__(self) -> None:
        self._settings = QSettings(ORG_NAME, APP_NAME)

    # ── helpers ──────────────────────────────────────────────────────────

    def _get(self, key: str, default: str = "") -> str:
        return str(self._settings.value(key, default))

    def _set(self, key: str, value: str) -> None:
        self._settings.setValue(key, value)

    # ── public properties ────────────────────────────────────────────────

    @property
    def api_key(self) -> str:
        return self._get("api_key")

    @api_key.setter
    def api_key(self, value: str) -> None:
        self._set("api_key", value)

    @property
    def from_email(self) -> str:
        return self._get("from_email")

    @from_email.setter
    def from_email(self, value: str) -> None:
        self._set("from_email", value)

    @property
    def from_name(self) -> str:
        return self._get("from_name")

    @from_name.setter
    def from_name(self, value: str) -> None:
        self._set("from_name", value)

    @property
    def subject(self) -> str:
        return self._get("subject")

    @subject.setter
    def subject(self, value: str) -> None:
        self._set("subject", value)

    @property
    def reply_to(self) -> str:
        return self._get("reply_to")

    @reply_to.setter
    def reply_to(self, value: str) -> None:
        self._set("reply_to", value)

    @property
    def delay_seconds(self) -> float:
        val = self._settings.value("delay_seconds", 5.0)
        try:
            return float(val)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 5.0

    @delay_seconds.setter
    def delay_seconds(self, value: float) -> None:
        self._settings.setValue("delay_seconds", value)

    @property
    def html_body(self) -> str:
        return self._get("html_body")

    @html_body.setter
    def html_body(self, value: str) -> None:
        self._set("html_body", value)
