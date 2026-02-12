"""Background worker that sends emails one-by-one via Resend with rate-limiting."""

from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass
from typing import List

import resend
from bs4 import BeautifulSoup
from PyQt6.QtCore import QThread, pyqtSignal


# ── data types ───────────────────────────────────────────────────────────────

@dataclass
class EmailResult:
    """Outcome of a single send attempt."""

    recipient: str
    success: bool
    message: str  # resend id on success, error text on failure


# ── helpers ──────────────────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def is_valid_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(email.strip()))


def html_to_plain_text(html: str) -> str:
    """Convert HTML to a readable plain-text fallback (anti-spam best practice)."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove script / style tags entirely
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ── worker ───────────────────────────────────────────────────────────────────

class EmailSenderWorker(QThread):
    """
    Sends emails sequentially with a configurable delay between each send.

    Anti-spam best practices applied:
    - Plain-text alternative auto-generated from HTML
    - Slight random jitter on delay to avoid robotic patterns
    - Proper 'from' formatting  (Name <email>)
    - Reply-To header when provided
    - List-Unsubscribe header
    - One recipient per API call (avoids bulk-flag triggers)
    """

    # ── signals ──────────────────────────────────────────────────────────
    progress = pyqtSignal(int, int)            # (current_index, total)
    email_sent = pyqtSignal(object)            # EmailResult
    finished_all = pyqtSignal(int, int)        # (success_count, fail_count)
    log_message = pyqtSignal(str)              # informational log line
    error_occurred = pyqtSignal(str)           # fatal / config error

    def __init__(
        self,
        api_key: str,
        from_name: str,
        from_email: str,
        subject: str,
        html_body: str,
        recipients: List[str],
        delay_seconds: float = 5.0,
        reply_to: str = "",
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.api_key = api_key.strip()
        self.from_name = from_name.strip()
        self.from_email = from_email.strip()
        self.subject = subject.strip()
        self.html_body = html_body
        self.recipients = recipients
        self.delay_seconds = max(delay_seconds, 1.0)  # floor at 1 s
        self.reply_to = reply_to.strip()

        self._stop_requested = False

    # ── public ───────────────────────────────────────────────────────────

    def request_stop(self) -> None:
        self._stop_requested = True

    # ── main loop ────────────────────────────────────────────────────────

    def run(self) -> None:  # noqa: C901 – acceptable for a worker
        # Validate inputs
        if not self.api_key:
            self.error_occurred.emit("API key is empty.")
            return
        if not self.from_email:
            self.error_occurred.emit("Sender email is empty.")
            return
        if not self.subject:
            self.error_occurred.emit("Subject line is empty.")
            return
        if not self.html_body.strip():
            self.error_occurred.emit("Email body (HTML) is empty.")
            return
        if not self.recipients:
            self.error_occurred.emit("Recipient list is empty.")
            return

        resend.api_key = self.api_key

        # Build the "from" field: "Name <email>" or just email
        sender = (
            f"{self.from_name} <{self.from_email}>"
            if self.from_name
            else self.from_email
        )

        # Generate plain-text alternative once
        plain_text = html_to_plain_text(self.html_body)

        total = len(self.recipients)
        success_count = 0
        fail_count = 0

        self.log_message.emit(
            f"Starting to send {total} email(s) with ~{self.delay_seconds}s delay…"
        )

        for idx, recipient in enumerate(self.recipients):
            if self._stop_requested:
                self.log_message.emit("Sending stopped by user.")
                break

            recipient = recipient.strip()
            if not recipient:
                continue

            if not is_valid_email(recipient):
                result = EmailResult(recipient, False, "Invalid email format")
                self.email_sent.emit(result)
                fail_count += 1
                self.progress.emit(idx + 1, total)
                continue

            # ── build params ─────────────────────────────────────────
            params: resend.Emails.SendParams = {
                "from": sender,
                "to": [recipient],
                "subject": self.subject,
                "html": self.html_body,
                "text": plain_text,
                "headers": {
                    "List-Unsubscribe": f"<mailto:{self.from_email}?subject=unsubscribe>",
                    "X-Entity-Ref-ID": f"bulk-{int(time.time())}-{idx}",
                },
                "tags": [
                    {"name": "campaign", "value": "bulk_send"},
                    {"name": "batch_index", "value": str(idx)},
                ],
            }

            if self.reply_to:
                params["reply_to"] = self.reply_to

            # ── send ─────────────────────────────────────────────────
            try:
                response = resend.Emails.send(params)
                email_id = response.get("id", "unknown") if isinstance(response, dict) else str(response)
                result = EmailResult(recipient, True, email_id)
                success_count += 1
                self.log_message.emit(
                    f"[{idx + 1}/{total}] ✓ {recipient} → {email_id}"
                )
            except Exception as exc:
                result = EmailResult(recipient, False, str(exc))
                fail_count += 1
                self.log_message.emit(
                    f"[{idx + 1}/{total}] ✗ {recipient} → {exc}"
                )

            self.email_sent.emit(result)
            self.progress.emit(idx + 1, total)

            # ── rate-limit delay with jitter ─────────────────────────
            if idx < total - 1 and not self._stop_requested:
                jitter = random.uniform(-0.5, 0.5)
                sleep_time = max(1.0, self.delay_seconds + jitter)
                self.log_message.emit(f"  waiting {sleep_time:.1f}s …")
                # Sleep in small increments so we can react to stop requests
                slept = 0.0
                while slept < sleep_time and not self._stop_requested:
                    step = min(0.25, sleep_time - slept)
                    time.sleep(step)
                    slept += step

        self.finished_all.emit(success_count, fail_count)
