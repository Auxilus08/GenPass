# GenPass

GenPass is a Python desktop password manager (Tkinter) with encrypted storage, two-factor authentication, and email-based OTP verification. It ships with a simple GUI, sensible defaults, and optional Docker packaging.

## Features
- Password generation with selectable strength and length
- Encrypted storage backed by `cryptography` (AES/Fernet)
- Email OTP for 2FA and account verification
- Theme preference persistence (light/dark)
- Clipboard copy helpers and strength feedback

## Tech Stack
- Python 3.11, Tkinter UI
- `cryptography`, `pyotp`, `pyperclip`
- Logging to `genpass.log`

## Directory Layout
- `run.py`: CLI entry that boots the Tkinter app
- `src/`: application code
- `config/`: user-supplied settings (created if missing)
- `data/`: runtime data store (created if missing)

## Prerequisites
- Local: Python 3.8+ with Tk available, `pip`
- Docker option: Docker and Docker Compose (v2). For X11 passthrough on Linux, `xhost` access to your display may be required.

## Quickstart (Local)
1) Create a virtual environment and install deps
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2) Configure outgoing email (needed for OTP). Create or edit `config/email_config.json`:
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "your-email@gmail.com",
  "sender_password": "your-app-password"
}
```
3) Run the app
```bash
python run.py
```
On first launch, `config/` and `data/` are created automatically. Logs go to `genpass.log`.

## Quickstart (Docker)
The Docker image bundles Tkinter and Xvfb so the GUI can start inside the container. To see the UI on your host, allow X11 and share your display.

```bash
# from repo root
cd src
# allow local docker to access X11 (Linux)
xhost +local:docker
# launch
DISPLAY=${DISPLAY:-:0} docker compose up --build
```
Notes:
- The compose file lives in `src/docker-compose.yml` and builds using the repo root as context.
- Config and data persist via bind mounts: `../config` -> `/app/config`.
- If you prefer the built-in virtual display, keep the default `DISPLAY=:99`; if you want host rendering, override the command, e.g.:
```bash
docker compose run --rm -e DISPLAY=$DISPLAY genpass python run.py
```

## Usage Tips
- Register then verify via the emailed OTP to access the vault.
- Passwords and preferences live under `data/` and `config/`; back them up to preserve your vault.
- If dependencies are missing, the app shows a dialog pointing to `pip install -r requirements.txt`.

## Troubleshooting
- GUI does not appear in Docker: ensure your host X server allows local connections (`xhost +local:docker`) and that `DISPLAY` matches your host (often `:0`).
- Email send fails: verify SMTP host/port and that you are using an app password when required (e.g., Gmail).
- Tkinter missing locally: install your OS Tk package (e.g., `sudo apt-get install python3-tk`).



