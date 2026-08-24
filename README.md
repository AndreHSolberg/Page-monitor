# Page Monitor

A small scheduled script that checks a web page for a change and sends a
notification (email / push) when it happens.

## Setup

1. Add these repository secrets under **Settings → Secrets and variables →
   Actions**:

| Secret | Description |
|---|---|
| `TARGET_URL` | The page to monitor |
| `TARGET_PHRASE` | Text that indicates "nothing to report" — a notification fires when this phrase disappears from the page |
| `EMAIL_FROM` | Sender email address |
| `EMAIL_APP_PASSWORD` | App password for the sender account |
| `EMAIL_TO` | Recipient email address |
| `NOTIFY_TOPIC` | Push notification topic (via ntfy.sh) |

2. Go to the **Actions** tab and run the workflow manually once to confirm
   it works, or wait for the schedule.

3. Subscribe to your chosen topic name in the ntfy app to receive push
   notifications.

The workflow runs on a schedule (see `.github/workflows/check.yml`) and
commits its last-known state back to the repo so it doesn't repeat
notifications.
