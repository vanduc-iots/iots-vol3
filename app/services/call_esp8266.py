import requests
import time
import os

# ESP8266 Configuration
ESP8266_HOST = os.getenv("ESP8266_HOST", "10.141.235.134")
REQUEST_TIMEOUT = 5
MAX_RETRY = 3

def light_control(status=None, led="all"):
    """
    status: on | off | toggle
    led: 1 | 2 | all
    """

    # ===== 1. Kiểm tra đầu vào =====
    if not status:
        return {
            "content": "Không có lệnh điều khiển mới.",
            "image": []
        }

    status = str(status).lower().strip()
    led = str(led).lower().strip()

    if status not in ["on", "off", "toggle"]:
        return {
            "content": f"Lệnh không hợp lệ: {status}",
            "image": []
        }

    if led not in ["1", "2", "all"]:
        led = "all"

    leds_to_control = ["1", "2"] if led == "all" else [led]
    led_statuses = {}
    last_error = ""

    # ===== 2. Gửi lệnh điều khiển =====
    for l in leds_to_control:
        if status == "toggle":
            url = f"http://{ESP8266_HOST}/led{l}/toggle"
        else:
            url = f"http://{ESP8266_HOST}/led{l}/{status}"

        led_status = None

        for attempt in range(MAX_RETRY):
            try:
                print(f"[light_control] Attempt {attempt+1}: {url}")
                response = requests.get(url, timeout=REQUEST_TIMEOUT)

                if response.status_code == 200:
                    # ESP trả dạng: LED1=ON
                    for line in response.text.strip().split("\n"):
                        if line.startswith(f"LED{l}="):
                            led_status = line.split("=")[1]
                            break

                    # Nếu toggle mà ESP không trả trạng thái
                    if status == "toggle" and not led_status:
                        led_status = "CHANGED"

                    break
                else:
                    last_error = f"HTTP {response.status_code}"

            except requests.exceptions.Timeout:
                last_error = "Timeout khi kết nối ESP"
            except requests.exceptions.ConnectionError:
                last_error = "Không kết nối được ESP"
            except Exception as e:
                last_error = str(e)

            time.sleep(1)

        led_statuses[l] = led_status

    # ===== 3. Tạo phản hồi chatbot =====
    if any(v is None for v in led_statuses.values()):
        return {
            "content": f"Lỗi điều khiển đèn: {last_error}",
            "image": []
        }

    action_text = {
        "on": "bật",
        "off": "tắt",
        "toggle": "chuyển đổi trạng thái"
    }[status]

    led_text = "tất cả đèn" if led == "all" else f"đèn {led}"
    status_text = ", ".join([f"đèn {k}: {v}" for k, v in led_statuses.items()])

    return {
        "content": f"Đã {action_text} {led_text}. Trạng thái: {status_text}.",
        "image": []
    }
