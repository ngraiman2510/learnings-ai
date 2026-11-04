import argparse
import logging
import re
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zipfile import BadZipFile

import openpyxl
import pyautogui
import pyperclip
from openpyxl.utils.exceptions import InvalidFileException

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
# ----------------------------- settings ------------------------------------ #
CHROME = "Google Chrome"
NUMBERS = "Numbers"
TEMP_PATTERN = re.compile(
    r"[-+]?\d+(?:\.\d+)?\s*°\s*[CF]?", re.IGNORECASE
)  # e.g. +30°C
START_DELAY = 5  # seconds to take your hands off the mouse
PAGE_WAIT = 4  # base seconds to wait for the page (grows each retry)
RETRIES = 4  # attempts to copy valid data (handles slow pages)
FILE_TIMEOUT = 30  # seconds to wait for the .xlsx to be saved

pyautogui.PAUSE = 0.4
pyautogui.FAILSAFE = True

log = logging.getLogger("bot")


class BotError(Exception):
    """Every problem the bot detects is raised as this error."""


# ----------------------------- helpers ------------------------------------- #
def osa(*lines, check=True):
    """Run AppleScript lines; return stdout. Raises BotError on failure."""
    cmd = ["osascript"]
    for line in lines:
        cmd += ["-e", line]
    run = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if check and run.returncode != 0:
        raise BotError(
            f"AppleScript failed: {run.stderr.strip()}  "
            "(Check Accessibility/Automation permission for your Terminal.)"
        )
    return run.stdout.strip()


def activate(app, timeout=20):
    """Bring `app` to the front and confirm it really is the front app."""
    end = time.time() + timeout
    while time.time() < end:
        osa(f'tell application "{app}" to activate', check=False)
        time.sleep(1)
        front = osa(
            'tell application "System Events" to get name of '
            "first application process whose frontmost is true"
        )
        if front == app:
            return
    raise BotError(f"{app} did not come to the front within {timeout}s.")


def check_internet(host="www.accuweather.com"):
    try:
        socket.create_connection((host, 443), timeout=5).close()
    except OSError as exc:
        raise BotError(f"Cannot reach AccuWeather ({host}): {exc}")


def open_numbers():
    pyautogui.hotkey("command", "space")
    time.sleep(1)
    pyautogui.write("Numbers", interval=0.1)
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(5)


def preflight(out_dir):
    for app in (CHROME,):
        result = subprocess.run(
            [
                "osascript",
                "-e",
                f'POSIX path of (path to application "{app}")',
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise BotError(f"{app} was not found: {result.stderr.strip()}")

    check_internet()
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / ".test").write_text("ok")
        (out_dir / ".test").unlink()
    except OSError as exc:
        raise BotError(f"Output folder not writable: {out_dir} ({exc})")


# ----------------------------- step 1: Chrome ------------------------------ #
def fetch_weather(url):
    log.info("Opening Chrome: %s", url)
    if subprocess.run(["open", "-a", CHROME, url], check=False).returncode != 0:
        raise BotError("Could not open Chrome.")

    width, height = pyautogui.size()
    copied_text = "__EMPTY__"
    for attempt in range(1, RETRIES + 1):
        log.info("Waiting for page (attempt %d/%d)", attempt, RETRIES)
        time.sleep(PAGE_WAIT * attempt)  # slower page -> wait longer
        activate(CHROME)
        osa(
            f'tell application "Google Chrome" to set bounds of front window '
            f"to {{0, 0, {width}, {height}}}",
            check=False,
        )

        pyautogui.click(width // 2, height // 2)  # focus the page
        pyperclip.copy("__EMPTY__")  # detect a failed copy
        pyautogui.hotkey("command", "a")
        pyautogui.hotkey("command", "c")
        time.sleep(0.5)

        copied_text = pyperclip.paste()
        lines = [" ".join(line.split()) for line in copied_text.splitlines()]
        matches = [
            (index, line)
            for index, line in enumerate(lines)
            if TEMP_PATTERN.search(line)
        ]

        current_index = next(
            (
                index
                for index, line in enumerate(lines)
                if "current weather" in line.lower()
            ),
            None,
        )
        if current_index is not None:
            nearby = [
                line
                for index, line in matches
                if current_index <= index <= current_index + 8
            ]
            if nearby:
                log.info("Fetched from AccuWeather: %s", nearby[0])
                return nearby[0]

        if matches:
            data = matches[0][1]
            log.info("Fetched from AccuWeather: %s", data)
            return data

    if copied_text == "__EMPTY__":
        raise BotError(
            "Chrome did not copy page text to the clipboard. Check that the page "
            "is loaded and focused, and that macOS allows Accessibility control."
        )

    current_weather = next(
        (line for line in lines if "current weather" in line.lower()), None
    )
    preview = current_weather or " ".join(lines)[:300]
    raise BotError(
        "Copied AccuWeather page text, but found no temperature. The page may "
        f"show a consent/block page or have changed format. Copied text preview: {preview!r}"
    )


def make_comment(data):
    if re.search(r"rain|storm|thunder|drizzle|shower", data, re.IGNORECASE):
        return "Wet weather - carry an umbrella"
    m = re.search(r"([-+]?\d+(?:\.\d+)?)\s*°\s*([CF])?", data, re.IGNORECASE)
    if not m:
        return "Data captured"
    t = float(m.group(1))
    unit = (m.group(2) or "C").upper()
    if unit == "F":
        t = (t - 32) * 5 / 9
    if t < 15:
        return "Cool - carry a jacket"
    if t <= 26:
        return "Good for outdoor activities"
    if t <= 33:
        return "Warm - stay hydrated"
    return "Very hot - avoid midday outdoor work"


# ----------------------------- step 2: Numbers ----------------------------- #
def select_cell(ref):
    osa(
        'tell application "Numbers"',
        "tell front document",
        "tell active sheet",
        "tell table 1",
        f'set selection range to range "{ref}"',
        "end tell",
        "end tell",
        "end tell",
        "end tell",
    )


def put(ref, text):
    select_cell(ref)
    pyperclip.copy(text)  # paste handles ° and other symbols
    pyautogui.hotkey("command", "v")
    time.sleep(0.4)


def fill_numbers(row):
    # Open Numbers with Spotlight, then create a blank sheet.
    pyautogui.hotkey("command", "space")
    time.sleep(1)
    pyautogui.write("Numbers", interval=0.1)
    pyautogui.press("enter")
    time.sleep(6)

    pyautogui.hotkey("command", "n")
    time.sleep(2)
    pyautogui.press("enter")  # choose the default blank template
    time.sleep(4)

    activate(NUMBERS)
    select_cell("A1")

    # Paste the header and report row starting at A1.
    pyperclip.copy("Date & Time\tFetched Data\tComment\n" + "\t".join(row))
    pyautogui.hotkey("command", "v")
    time.sleep(2)


def save_report(path, now, data, comment):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Daily Report"
    ws.append(["Date & Time", "Fetched Data", "Comment"])
    ws.append([now, data, comment])
    ws.freeze_panes = "A2"
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 38
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def screenshot(path):
    activate(NUMBERS)
    time.sleep(1)
    try:
        pyautogui.screenshot().save(str(path))
    except OSError as exc:
        raise BotError(f"Could not save screenshot: {exc}")
    if not path.exists() or path.stat().st_size == 0:
        raise BotError("Screenshot file is empty.")
    log.info("Screenshot saved: %s", path)


# ----------------------------- step 5: verify ------------------------------ #
def verify(path, today, data, comment):
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
    except (OSError, BadZipFile, InvalidFileException) as exc:
        raise BotError(f"Saved file is not a valid .xlsx: {exc}")
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            cells = [c for c in row if c is not None]
            texts = [str(c).strip() for c in cells]
            if data in texts and comment in texts:
                stamp = cells[0]
                ok = (
                    stamp.date() == today.date()
                    if isinstance(stamp, datetime)
                    else str(stamp).startswith(today.strftime("%Y-%m-%d"))
                )
                if not ok:
                    raise BotError(f"Date cell is wrong: {stamp!r}")
                log.info("Verified row: %s", cells)
                return
    raise BotError("Verification failed: the new row was not found in the .xlsx.")


# ----------------------------- main ---------------------------------------- #
def run(args):
    out_dir = Path(args.out_dir).expanduser().resolve()
    preflight(out_dir)

    log.info("Starting in %ds - hands off! (mouse to a corner = stop)", START_DELAY)
    time.sleep(START_DELAY)

    now = datetime.now()  # auto date & time
    stem = f"daily_report_{now:%Y-%m-%d}"
    if (out_dir / f"{stem}.xlsx").exists():  # don't overwrite an old run
        stem += f"_{now:%H%M%S}"
    xlsx, png = out_dir / f"{stem}.xlsx", out_dir / f"{stem}_screenshot.png"

    url = "https://www.accuweather.com/en/in/coimbatore/206673/weather-forecast/206673"
    data = fetch_weather(url)
    pyautogui.hotkey("command", "w")  # close the Chrome tab

    comment = make_comment(data)
    fill_numbers([now.strftime("%Y-%m-%d %H:%M:%S"), data, comment])
    screenshot(png)
    save_report(xlsx, now, data, comment)
    osa('tell application "Numbers" to close front document saving no', check=False)
    verify(xlsx, now, data, comment)
    log.info("DONE -> %s and %s", xlsx, png)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    p = argparse.ArgumentParser()
    p.add_argument("--city", default="Coimbatore")
    p.add_argument("--out-dir", default="~/Downloads")
    args = p.parse_args()
    try:
        run(args)
    except BotError as exc:
        log.error("%s", exc)
        sys.exit(1)
    except pyautogui.FailSafeException:
        log.error("Stopped: mouse moved to a screen corner (fail-safe).")
        sys.exit(130)
    except KeyboardInterrupt:
        log.error("Stopped by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()
