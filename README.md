# Bulk Email Sender (Resend)

A desktop application for sending bulk emails via [Resend](https://resend.com) with a modern PyQt6 UI, live HTML preview, and anti-spam optimisations.

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)

## Features

- **One-by-one sending** with configurable delay (default 5 s) to avoid rate-limit and spam triggers
- **Anti-spam best practices** baked in:
  - Automatic **plain-text fallback** generated from your HTML
  - **List-Unsubscribe** header on every email
  - Unique **X-Entity-Ref-ID** per message
  - Random **jitter** on the delay to avoid robotic send patterns
  - One recipient per API call (no BCC blasting)
- **HTML editor with live preview** (side-by-side, debounced)
- **Load recipients** from a `.txt` / `.csv` file (one email per line) or paste directly
- **Progress bar**, per-email log, and estimated-time confirmation dialog
- **Persistent settings** — API key, sender info, subject, and HTML body are saved between sessions
- **Stop button** — gracefully stop mid-send at any time

## Requirements

- Python **3.10+**
- A [Resend](https://resend.com) account with a **verified domain** (SPF + DKIM configured automatically by Resend)

## Installation

```bash
# Clone
git clone https://github.com/your-user/bulk-email-sender-resend.git
cd bulk-email-sender-resend

# Create virtual env (recommended)
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

> **Note:** `PyQt6-WebEngine` is pulled in automatically by `PyQt6` for the live HTML preview.

## Usage

```bash
python main.py
```

1. Enter your **Resend API key** (starts with `re_`).
2. Fill in **From Name**, **From Email** (must match your verified domain), and optionally **Reply-To**.
3. Write the **Subject**.
4. Paste or author your **HTML** in the editor — the right pane shows a live preview.
5. Add recipients — paste emails (one per line) or click **Load .txt File**.
6. Set the **delay** between sends (5 s recommended; minimum 1 s).
7. Click **Start Sending** and confirm.

The log area shows real-time results. Click **Stop** at any time to abort.

## Anti-Spam Tips

| Area | Recommendation |
|---|---|
| **Domain** | Use a verified custom domain in Resend (not `@resend.dev`). |
| **SPF / DKIM / DMARC** | Resend auto-configures SPF & DKIM. Add a DMARC record (`v=DMARC1; p=none;`) for extra trust. |
| **Content** | Avoid ALL-CAPS subjects, excessive exclamation marks, and spam trigger words. |
| **HTML** | Keep HTML clean — no invisible text, no image-only emails. This app auto-generates a plain-text fallback. |
| **Volume** | Start slow (50-100 emails/day) and ramp up over 2-4 weeks ("IP warming"). |
| **Unsubscribe** | The app adds a `List-Unsubscribe` header automatically. |
| **Reply-To** | Set a monitored Reply-To address to improve sender reputation. |

## Project Structure

```
bulk-email-sender-resend/
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── core/
│   ├── __init__.py
│   ├── config.py            # QSettings-based persistence
│   └── email_sender.py      # QThread worker + anti-spam logic
└── ui/
    ├── __init__.py
    ├── html_preview.py      # Side-by-side HTML editor + WebEngine preview
    └── main_window.py       # Main window layout and signals
```

## License

MIT
