"""Main application window – all UI layout and event wiring."""

from __future__ import annotations

import os
from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QDoubleSpinBox,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.config import AppConfig
from core.email_sender import EmailSenderWorker, EmailResult
from ui.html_preview import HtmlEditorWidget


# ── Stylesheet ───────────────────────────────────────────────────────────────

STYLESHEET = """
* {
    font-family: 'SF Pro Display', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
}

QMainWindow {
    background-color: #0f0f14;
}

QWidget#centralWidget {
    background-color: #0f0f14;
}

QScrollArea {
    background-color: #0f0f14;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background-color: #0f0f14;
}

/* ── Group Boxes ─────────────────────────────────────────── */
QGroupBox {
    background-color: #16161e;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    margin-top: 20px;
    padding: 20px 16px 16px 16px;
    font-size: 13px;
    font-weight: 600;
    color: #c0caf5;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 2px 10px;
    color: #7aa2f7;
    font-size: 13px;
}

/* ── Inputs ──────────────────────────────────────────────── */
QLineEdit {
    background-color: #1a1b26;
    border: 1px solid #292e42;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #c0caf5;
    selection-background-color: #33467c;
    min-height: 18px;
}
QLineEdit:focus {
    border: 1px solid #7aa2f7;
    background-color: #1e2030;
}
QLineEdit:hover {
    border: 1px solid #3b4261;
}
QLineEdit::placeholder {
    color: #565f89;
}

QDoubleSpinBox {
    background-color: #1a1b26;
    border: 1px solid #292e42;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #c0caf5;
    min-height: 18px;
}
QDoubleSpinBox:focus {
    border: 1px solid #7aa2f7;
}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    width: 20px;
    border: none;
    background: #292e42;
    border-radius: 4px;
    margin: 2px;
}
QDoubleSpinBox::up-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #7aa2f7;
    width: 0; height: 0;
}
QDoubleSpinBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #7aa2f7;
    width: 0; height: 0;
}

/* ── Text areas ──────────────────────────────────────────── */
QPlainTextEdit {
    background-color: #1a1b26;
    border: 1px solid #292e42;
    border-radius: 8px;
    padding: 10px;
    font-size: 13px;
    color: #c0caf5;
    selection-background-color: #33467c;
    line-height: 1.5;
}
QPlainTextEdit:focus {
    border: 1px solid #7aa2f7;
}

QTextEdit#logView {
    background-color: #1a1b26;
    color: #9aa5ce;
    border: 1px solid #292e42;
    border-radius: 8px;
    padding: 10px;
    font-size: 12px;
}

/* ── Buttons ─────────────────────────────────────────────── */
QPushButton {
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 13px;
    min-height: 16px;
}

QPushButton#sendBtn {
    background-color: #7aa2f7;
    color: #1a1b26;
}
QPushButton#sendBtn:hover {
    background-color: #89b4fa;
}
QPushButton#sendBtn:pressed {
    background-color: #6d8fd4;
}
QPushButton#sendBtn:disabled {
    background-color: #292e42;
    color: #565f89;
}

QPushButton#stopBtn {
    background-color: #f7768e;
    color: #1a1b26;
}
QPushButton#stopBtn:hover {
    background-color: #ff9e9e;
}
QPushButton#stopBtn:disabled {
    background-color: #292e42;
    color: #565f89;
}

QPushButton#loadFileBtn {
    background-color: #9ece6a;
    color: #1a1b26;
}
QPushButton#loadFileBtn:hover {
    background-color: #afd68a;
}

QPushButton#clearListBtn {
    background-color: #292e42;
    color: #9aa5ce;
}
QPushButton#clearListBtn:hover {
    background-color: #3b4261;
    color: #c0caf5;
}

/* ── Progress Bar ────────────────────────────────────────── */
QProgressBar {
    border: none;
    border-radius: 6px;
    text-align: center;
    background-color: #1a1b26;
    color: #c0caf5;
    font-size: 11px;
    font-weight: 600;
    max-height: 14px;
    min-height: 14px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7aa2f7, stop:1 #9ece6a);
    border-radius: 6px;
}

/* ── Labels ──────────────────────────────────────────────── */
QLabel#fieldLabel {
    font-size: 12px;
    font-weight: 500;
    color: #9aa5ce;
    padding-bottom: 2px;
    background: transparent;
}
QLabel#countLabel {
    font-size: 12px;
    color: #565f89;
    background: transparent;
}
QLabel#progressText {
    font-size: 12px;
    color: #565f89;
    background: transparent;
}

/* ── Status Bar ──────────────────────────────────────────── */
QStatusBar {
    background-color: #13131a;
    color: #565f89;
    border-top: 1px solid #1e1e2e;
    font-size: 12px;
    padding: 4px 12px;
}
"""


class MainWindow(QMainWindow):
    """Top-level window for the Bulk Email Sender."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Bulk Email Sender — Resend")
        self.setMinimumSize(900, 700)
        self.resize(1060, 820)

        self.config = AppConfig()
        self._worker: Optional[EmailSenderWorker] = None

        self._build_ui()
        self._restore_fields()
        self.setStyleSheet(STYLESHEET)

    # =====================================================================
    #  UI construction
    # =====================================================================

    def _build_ui(self) -> None:
        # Scrollable central area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setCentralWidget(scroll)

        central = QWidget()
        central.setObjectName("centralWidget")
        scroll.setWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(28, 20, 28, 16)
        root.setSpacing(0)

        # ── Header ───────────────────────────────────────────────────
        header = QLabel("Bulk Email Sender")
        header.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #c0caf5;"
            "background: transparent; padding: 0; margin: 0;"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        root.addWidget(header)

        sub = QLabel("Send emails via Resend with anti-spam optimisations")
        sub.setStyleSheet(
            "font-size: 13px; color: #565f89; background: transparent;"
            "padding: 0; margin: 0 0 8px 0;"
        )
        root.addWidget(sub)

        # ── Row 1: Settings + Recipients side by side ────────────────
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        # -- Settings --
        settings_box = QGroupBox("Settings")
        sf = QVBoxLayout(settings_box)
        sf.setSpacing(12)
        sf.setContentsMargins(16, 24, 16, 16)

        self.api_key_input = self._add_field(sf, "API Key", placeholder="re_xxxxxxxx…", password=True)
        self.from_name_input = self._add_field(sf, "From Name", placeholder="My Company")
        self.from_email_input = self._add_field(sf, "From Email", placeholder="hello@yourdomain.com")
        self.reply_to_input = self._add_field(sf, "Reply-To", placeholder="support@yourdomain.com (optional)")
        self.subject_input = self._add_field(sf, "Subject", placeholder="Your email subject")

        # Delay
        delay_label = QLabel("Delay Between Emails")
        delay_label.setObjectName("fieldLabel")
        sf.addWidget(delay_label)
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(1.0, 60.0)
        self.delay_spin.setValue(5.0)
        self.delay_spin.setSingleStep(0.5)
        self.delay_spin.setSuffix("  sec")
        sf.addWidget(self.delay_spin)

        settings_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        row1.addWidget(settings_box, stretch=4)

        # -- Recipients --
        recip_box = QGroupBox("Recipients")
        rf = QVBoxLayout(recip_box)
        rf.setSpacing(8)
        rf.setContentsMargins(16, 24, 16, 16)

        hint = QLabel("One email per line, or load from a file")
        hint.setObjectName("fieldLabel")
        rf.addWidget(hint)

        self.recipient_edit = QPlainTextEdit()
        self.recipient_edit.setPlaceholderText(
            "alice@example.com\nbob@example.com\ncharlie@example.com"
        )
        self.recipient_edit.setFont(QFont("Menlo", 12))
        self.recipient_edit.setMinimumHeight(140)
        rf.addWidget(self.recipient_edit, stretch=1)

        # Buttons row
        rbtn = QHBoxLayout()
        rbtn.setSpacing(8)

        self.load_file_btn = QPushButton("Load File")
        self.load_file_btn.setObjectName("loadFileBtn")
        self.load_file_btn.clicked.connect(self._load_recipients_file)
        rbtn.addWidget(self.load_file_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("clearListBtn")
        self.clear_btn.clicked.connect(lambda: self.recipient_edit.clear())
        rbtn.addWidget(self.clear_btn)

        rbtn.addStretch()

        self.count_label = QLabel("0 recipients")
        self.count_label.setObjectName("countLabel")
        rbtn.addWidget(self.count_label)

        rf.addLayout(rbtn)
        recip_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        row1.addWidget(recip_box, stretch=5)

        root.addLayout(row1)

        # ── Row 2: HTML Editor ───────────────────────────────────────
        html_box = QGroupBox("Email Body")
        hf = QVBoxLayout(html_box)
        hf.setContentsMargins(16, 24, 16, 16)
        self.html_editor = HtmlEditorWidget()
        self.html_editor.setMinimumHeight(220)
        hf.addWidget(self.html_editor)
        root.addWidget(html_box, stretch=1)

        # ── Row 3: Actions ───────────────────────────────────────────
        action_box = QGroupBox("Send")
        af = QVBoxLayout(action_box)
        af.setSpacing(10)
        af.setContentsMargins(16, 24, 16, 16)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.send_btn = QPushButton("Start Sending")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.clicked.connect(self._on_send)
        btn_row.addWidget(self.send_btn, stretch=3)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        btn_row.addWidget(self.stop_btn, stretch=1)

        af.addLayout(btn_row)

        # Progress
        prog_row = QHBoxLayout()
        prog_row.setSpacing(10)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        prog_row.addWidget(self.progress_bar, stretch=1)

        self.progress_label = QLabel("Ready")
        self.progress_label.setObjectName("progressText")
        self.progress_label.setMinimumWidth(80)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prog_row.addWidget(self.progress_label)

        af.addLayout(prog_row)

        # Log
        log_label = QLabel("Log")
        log_label.setObjectName("fieldLabel")
        af.addWidget(log_label)

        self.log_view = QTextEdit()
        self.log_view.setObjectName("logView")
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Menlo", 11))
        self.log_view.setFixedHeight(130)
        af.addWidget(self.log_view)

        root.addWidget(action_box)

        # ── Status bar ───────────────────────────────────────────────
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # ── Live count ───────────────────────────────────────────────
        self.recipient_edit.textChanged.connect(self._update_count)

    # =====================================================================
    #  Helpers
    # =====================================================================

    @staticmethod
    def _add_field(
        layout: QVBoxLayout,
        label: str,
        placeholder: str = "",
        password: bool = False,
    ) -> QLineEdit:
        lbl = QLabel(label)
        lbl.setObjectName("fieldLabel")
        layout.addWidget(lbl)
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        if password:
            inp.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(inp)
        return inp

    def _get_recipients(self) -> List[str]:
        raw = self.recipient_edit.toPlainText()
        return [line.strip() for line in raw.splitlines() if line.strip()]

    def _update_count(self) -> None:
        n = len(self._get_recipients())
        self.count_label.setText(f"{n} recipient{'s' if n != 1 else ''}")

    # =====================================================================
    #  Persist / restore
    # =====================================================================

    def _restore_fields(self) -> None:
        self.api_key_input.setText(self.config.api_key)
        self.from_name_input.setText(self.config.from_name)
        self.from_email_input.setText(self.config.from_email)
        self.reply_to_input.setText(self.config.reply_to)
        self.subject_input.setText(self.config.subject)
        self.delay_spin.setValue(self.config.delay_seconds)
        self.html_editor.set_html(self.config.html_body)

    def _save_fields(self) -> None:
        self.config.api_key = self.api_key_input.text()
        self.config.from_name = self.from_name_input.text()
        self.config.from_email = self.from_email_input.text()
        self.config.reply_to = self.reply_to_input.text()
        self.config.subject = self.subject_input.text()
        self.config.delay_seconds = self.delay_spin.value()
        self.config.html_body = self.html_editor.get_html()

    def closeEvent(self, event) -> None:  # noqa: N802
        self._save_fields()
        if self._worker and self._worker.isRunning():
            self._worker.request_stop()
            self._worker.wait(3000)
        super().closeEvent(event)

    # =====================================================================
    #  File loader
    # =====================================================================

    def _load_recipients_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Recipients", "",
            "Text Files (*.txt);;CSV Files (*.csv);;All (*)",
        )
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as fh:
                self.recipient_edit.setPlainText(fh.read())
            self._log(f"Loaded {path}")
        except Exception as exc:
            QMessageBox.warning(self, "Error", f"Could not read file:\n{exc}")

    # =====================================================================
    #  Send / Stop
    # =====================================================================

    def _on_send(self) -> None:
        self._save_fields()

        recipients = self._get_recipients()
        if not recipients:
            QMessageBox.warning(self, "No Recipients", "Add at least one email address.")
            return

        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Missing API Key", "Enter your Resend API key.")
            return

        from_email = self.from_email_input.text().strip()
        if not from_email:
            QMessageBox.warning(self, "Missing Sender", "Enter the From email address.")
            return

        subject = self.subject_input.text().strip()
        if not subject:
            QMessageBox.warning(self, "Missing Subject", "Enter a subject line.")
            return

        html_body = self.html_editor.get_html()
        if not html_body.strip():
            QMessageBox.warning(self, "Empty Body", "Write or paste HTML email content.")
            return

        total = len(recipients)
        delay = self.delay_spin.value()
        est = total * delay
        m, s = int(est // 60), int(est % 60)

        answer = QMessageBox.question(
            self,
            "Confirm Send",
            f"Send to {total} recipient(s)?\n"
            f"Estimated time: {m}m {s}s\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self.log_view.clear()
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)
        self.progress_label.setText(f"0 / {total}")
        self.send_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self._worker = EmailSenderWorker(
            api_key=api_key,
            from_name=self.from_name_input.text().strip(),
            from_email=from_email,
            subject=subject,
            html_body=html_body,
            recipients=recipients,
            delay_seconds=delay,
            reply_to=self.reply_to_input.text().strip(),
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.email_sent.connect(self._on_email_sent)
        self._worker.finished_all.connect(self._on_finished)
        self._worker.log_message.connect(self._log)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.start()
        self.status_bar.showMessage("Sending…")

    def _on_stop(self) -> None:
        if self._worker:
            self._worker.request_stop()
            self.stop_btn.setEnabled(False)
            self._log("Stop requested — finishing current email…")
            self.status_bar.showMessage("Stopping…")

    # =====================================================================
    #  Worker signal handlers
    # =====================================================================

    def _on_progress(self, current: int, total: int) -> None:
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"{current} / {total}")

    def _on_email_sent(self, result: EmailResult) -> None:
        color = "#9ece6a" if result.success else "#f7768e"
        icon = "✓" if result.success else "✗"
        self.log_view.append(
            f'<span style="color:{color}">{icon} {result.recipient}</span>'
            f' — <span style="color:#565f89">{result.message}</span>'
        )

    def _on_finished(self, success: int, fail: int) -> None:
        self.send_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_bar.showMessage(f"Done — {success} sent, {fail} failed", 0)
        self._log(f"\nFinished: {success} sent, {fail} failed")
        QMessageBox.information(
            self, "Complete", f"Sent: {success}\nFailed: {fail}",
        )

    def _on_error(self, msg: str) -> None:
        self.send_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_bar.showMessage(f"Error: {msg}")
        QMessageBox.critical(self, "Error", msg)

    def _log(self, text: str) -> None:
        self.log_view.append(text)
        sb = self.log_view.verticalScrollBar()
        if sb:
            sb.setValue(sb.maximum())
