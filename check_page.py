import requests
import smtplib
import os
import sys
from email.mime.text import MIMEText
from datetime import datetime

TARGET_URL = os.environ.get("TARGET_URL", "")
TARGET_PHRASE = os.environ.get("TARGET_PHRASE", "")
STATE_FILE = "last_state.txt"

ENABLE_EMAIL = os.environ.get("ENABLE_EMAIL", "true").lower() == "true"
EMAIL_FROM = os.environ.get("EMAIL_FROM", "")
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD", "")
EMAIL_TO = os.environ.get("EMAIL_TO", "")

ENABLE_PUSH = os.environ.get("ENABLE_PUSH", "true").lower() == "true"
NOTIFY_TOPIC = os.environ.get("NOTIFY_TOPIC", "")

ENABLE_SMS = os.environ.get("ENABLE_SMS", "false").lower() == "true"
SMS_ACCOUNT_SID = os.environ.get("SMS_ACCOUNT_SID", "")
SMS_AUTH_TOKEN = os.environ.get("SMS_AUTH_TOKEN", "")
SMS_FROM_NUMBER = os.environ.get("SMS_FROM_NUMBER", "")
SMS_TO_NUMBER = os.environ.get("SMS_TO_NUMBER", "")


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fetch_page():
    headers = {"User-Agent": "Mozilla/5.0 (compatible; page-monitor; personal use)"}
    resp = requests.get(TARGET_URL, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.text


def condition_met(page_text):
    return TARGET_PHRASE not in page_text


def send_email(subject, body):
    if not ENABLE_EMAIL or not EMAIL_FROM:
        return
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_FROM, EMAIL_APP_PASSWORD)
            server.send_message(msg)
        print(f"[{timestamp()}] Email sent.")
    except Exception as e:
        print(f"[{timestamp()}] Email failed: {e}")


def send_push(title, body):
    if not ENABLE_PUSH or not NOTIFY_TOPIC:
        return
    try:
        requests.post(
            f"https://ntfy.sh/{NOTIFY_TOPIC}",
            data=body.encode("utf-8"),
            headers={"Title": title.encode("utf-8"), "Priority": "urgent"},
            timeout=10,
        )
        print(f"[{timestamp()}] Push sent.")
    except Exception as e:
        print(f"[{timestamp()}] Push failed: {e}")


def send_sms(body):
    if not ENABLE_SMS or not SMS_ACCOUNT_SID:
        return
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{SMS_ACCOUNT_SID}/Messages.json"
        resp = requests.post(
            url,
            data={"From": SMS_FROM_NUMBER, "To": SMS_TO_NUMBER, "Body": body},
            auth=(SMS_ACCOUNT_SID, SMS_AUTH_TOKEN),
            timeout=10,
        )
        resp.raise_for_status()
        print(f"[{timestamp()}] SMS sent.")
    except Exception as e:
        print(f"[{timestamp()}] SMS failed: {e}")


def read_last_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    return "unknown"


def save_state(state):
    with open(STATE_FILE, "w") as f:
        f.write(state)


def main():
    if not TARGET_URL or not TARGET_PHRASE:
        print(f"[{timestamp()}] Missing TARGET_URL or TARGET_PHRASE, aborting.")
        sys.exit(0)

    try:
        page_text = fetch_page()
    except Exception as e:
        print(f"[{timestamp()}] Fetch failed: {e}")
        sys.exit(0)

    triggered = condition_met(page_text)
    last_state = read_last_state()
    new_state = "triggered" if triggered else "not_triggered"

    if triggered:
        print(f"[{timestamp()}] Condition met.")
        if last_state != "triggered":
            title = "Update detected"
            body = "The page you're monitoring has changed."
            send_email(title, body)
            send_push(title, body)
            send_sms(body)
        else:
            print(f"[{timestamp()}] (Already notified, skipping.)")
    else:
        print(f"[{timestamp()}] No change.")

    save_state(new_state)


if __name__ == "__main__":
    main()
