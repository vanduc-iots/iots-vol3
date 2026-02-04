import requests
import time
import os

ESP8266_HOST = os.getenv("ESP8266_HOST", "10.216.4.134")
REQUEST_TIMEOUT = 5
MAX_RETRY = 3


def request_esp(url):
    """Gửi request tới ESP, có retry"""
    for _ in range(MAX_RETRY):
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                return r.text.strip()
        except:
            time.sleep(1)
    return None


def toggle_led(led):
    """Tắt/Mở 1 đèn"""
    status_url = f"https://{ESP8266_HOST}/led{led}/status"
    res = request_esp(status_url)

    if not res:
        return False, f"Lỗi đọc trạng thái đèn {led}"

    current = res.split("=")[1].lower()
    new_status = "off" if current == "on" else "on"

    action_url = f"https://{ESP8266_HOST}/led{led}/{new_status}"
    ok = request_esp(action_url)

    if ok:
        return True, f"Đèn {led}: {new_status.upper()}"
    return False, f"Lỗi điều khiển đèn {led}"


def set_all_led(status):
    """Bật/Tắt tất cả đèn"""
    url = f"https://{ESP8266_HOST}/ledall/{status}"
    ok = request_esp(url)

    if ok:
        return True, f"Tất cả đèn: {status.upper()}"
    return False, "Lỗi điều khiển tất cả đèn"


# ===== HÀM CHÍNH GỌI TỪ UI / CHATBOT =====
def light_control(action):
    """
    action:
    - toggle_1
    - toggle_2
    - on_all
    - off_all
    """

    if action == "toggle_1":
        ok, msg = toggle_led(1)

    elif action == "toggle_2":
        ok, msg = toggle_led(2)

    elif action == "on_all":
        ok, msg = set_all_led("on")

    elif action == "off_all":
        ok, msg = set_all_led("off")

    else:
        return {"content": "Hành động không hợp lệ", "image": []}

    if ok:
        return {"content": f"✅ {msg}", "image": []}
    else:
        return {"content": f"❌ {msg}", "image": []}
