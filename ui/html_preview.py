"""Side-by-side HTML code editor with live rendered preview."""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QSplitter,
    QVBoxLayout,
    QWidget,
)


class HtmlEditorWidget(QWidget):
    """A widget with an HTML code editor on the left and live preview on the right."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        # ── editor ───────────────────────────────────────────────────
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(4)

        editor_label = QLabel("HTML Code")
        editor_label.setStyleSheet(
            "font-weight: 600; font-size: 12px; color: #9aa5ce;"
            "background: transparent; padding: 0;"
        )
        editor_layout.addWidget(editor_label)

        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Menlo", 12))
        self.editor.setPlaceholderText("Paste or write your HTML email body here…")
        self.editor.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: #1a1b26;
                color: #c0caf5;
                border: 1px solid #292e42;
                border-radius: 8px;
                padding: 10px;
                selection-background-color: #33467c;
            }
            QPlainTextEdit:focus {
                border: 1px solid #7aa2f7;
            }
            """
        )
        editor_layout.addWidget(self.editor)

        # ── preview ──────────────────────────────────────────────────
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(4)

        preview_label = QLabel("Live Preview")
        preview_label.setStyleSheet(
            "font-weight: 600; font-size: 12px; color: #9aa5ce;"
            "background: transparent; padding: 0;"
        )
        preview_layout.addWidget(preview_label)

        self.preview = QWebEngineView()
        self.preview.setStyleSheet(
            "border: 1px solid #292e42; border-radius: 8px;"
        )
        preview_layout.addWidget(self.preview)

        # ── splitter ─────────────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(editor_container)
        splitter.addWidget(preview_container)
        splitter.setSizes([500, 500])
        splitter.setHandleWidth(3)
        splitter.setStyleSheet(
            "QSplitter::handle { background-color: #292e42; border-radius: 1px; }"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)

        # ── debounced preview refresh ────────────────────────────────
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(400)  # ms
        self._refresh_timer.timeout.connect(self._update_preview)
        self.editor.textChanged.connect(self._schedule_refresh)

    # ── helpers ──────────────────────────────────────────────────────────

    def _schedule_refresh(self) -> None:
        self._refresh_timer.start()

    def _update_preview(self) -> None:
        html = self.editor.toPlainText()
        wrapped = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    padding: 16px;
    margin: 0;
    color: #333;
    background: #fff;
    line-height: 1.6;
}}
img {{ max-width: 100%; height: auto; }}
</style>
</head><body>{html}</body></html>"""
        self.preview.setHtml(wrapped)

    def get_html(self) -> str:
        return self.editor.toPlainText()

    def set_html(self, html: str) -> None:
        self.editor.setPlainText(html)
        self._update_preview()
