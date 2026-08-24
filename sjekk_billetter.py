import requests
import smtplib
import os
import sys
from email.mime.text import MIMEText
from datetime import datetime

URL = "https://resale.fotball.no/list/resaleProducts/?lang=no"
INGEN_BILLETTER_TEKST = "There are currently no tickets being resold"
STATUS_FIL = "siste_status.txt"

ENABLE_EPOST = os.environ.get("ENABLE_EPOST", "true").lower() == "true"
EPOST_AVSENDER = os.environ.get("EPOST_AVSENDER", "")
EPOST_APP_PASSORD = os.environ.get("EPOST_APP_PASSORD", "")
EPOST_MOTTAKER = os.environ.get("EPOST_MOTTAKER", "")

ENABLE_PUSH = os.environ.get("ENABLE_PUSH", "true").lower() == "true"
NTFY_EMNE = os.environ.get("NTFY_EMNE", "")

ENABLE_SMS = os.environ.get("ENABLE_SMS", "false").lower() == "true"
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FRA_NUMMER = os.environ.get("TWILIO_FRA_NUMMER", "")
SMS_TIL_NUMMER = os.environ.get("SMS_TIL_NUMMER", "")


def tidsstempel():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def hent_side_tekst():
    headers = {"User-Agent": "Mozilla/5.0 (kompatibel billett-varsler; personlig bruk)"}
    respons = requests.get(URL, headers=headers, timeout=15)
    respons.raise_for_status()
    return respons.text


def er_billetter_tilgjengelig(side_tekst):
    return INGEN_BILLETTER_TEKST not in side_tekst


def send_epost(tittel, melding):
    if not ENABLE_EPOST or not EPOST_AVSENDER:
        return
    try:
        msg = MIMEText(melding)
        msg["Subject"] = tittel
        msg["From"] = EPOST_AVSENDER
        msg["To"] = EPOST_MOTTAKER
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EPOST_AVSENDER, EPOST_APP_PASSORD)
            server.send_message(msg)
        print(f"[{tidsstempel()}] E-post sendt.")
    except Exception as e:
        print(f"[{tidsstempel()}] Klarte ikke sende e-post: {e}")


def send_push(tittel, melding):
    if not ENABLE_PUSH or not NTFY_EMNE:
        return
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_EMNE}",
            data=melding.encode("utf-8"),
            headers={"Title": tittel.encode("utf-8"), "Priority": "urgent"},
            timeout=10,
        )
        print(f"[{tidsstempel()}] Push-varsel sendt.")
    except Exception as e:
        print(f"[{tidsstempel()}] Klarte ikke sende push: {e}")


def send_sms(melding):
    if not ENABLE_SMS or not TWILIO_ACCOUNT_SID:
        return
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        respons = requests.post(
            url,
            data={"From": TWILIO_FRA_NUMMER, "To": SMS_TIL_NUMMER, "Body": melding},
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=10,
        )
        respons.raise_for_status()
        print(f"[{tidsstempel()}] SMS sendt.")
    except Exception as e:
        print(f"[{tidsstempel()}] Klarte ikke sende SMS: {e}")


def les_forrige_status():
    if os.path.exists(STATUS_FIL):
        with open(STATUS_FIL, "r") as f:
            return f.read().strip()
    return "ukjent"


def lagre_status(status):
    with open(STATUS_FIL, "w") as f:
        f.write(status)


def main():
    try:
        side_tekst = hent_side_tekst()
    except Exception as e:
        print(f"[{tidsstempel()}] Feil ved henting av siden: {e}")
        sys.exit(0)

    billetter_na = er_billetter_tilgjengelig(side_tekst)
    forrige_status = les_forrige_status()
    ny_status = "billetter" if billetter_na else "ingen_billetter"

    if billetter_na:
        print(f"[{tidsstempel()}] Billetter ser ut til a vaere tilgjengelige!")
        if forrige_status != "billetter":
            tittel = "NFF resale-billetter tilgjengelig!"
            melding = f"Det ser ut som det er lagt ut billetter: {URL}"
            send_epost(tittel, melding)
            send_push(tittel, melding)
            send_sms(melding)
        else:
            print(f"[{tidsstempel()}] (Allerede varslet, sender ikke pa nytt.)")
    else:
        print(f"[{tidsstempel()}] Ingen billetter forelopig.")

    lagre_status(ny_status)


if __name__ == "__main__":
    main()
