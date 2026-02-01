import requests
import time

# ESP8266 Configuration
ESP8266_IP = "ungroundable-brigandishly-princeton.ngrok-free.dev"  # Ngrok tunnel URL
ESP8266_PORT = 443  # HTTPS port for ngrok
REQUEST_TIMEOUT = 5
MAX_RETRY = 3

def light_control(status="off", led="all"):
    """
    Điều khiển đèn LED trên ESP8266
    
    Args:
        status (str): "on" để bật đèn, "off" để tắt đèn
        led (str): "1", "2", hoặc "all" để chỉ định đèn
    
    Returns:
        dict: Chứa content (câu trả lời) và image (danh sách ảnh)
    """
    from ..bot import generate_Content
    
    status = status.lower().strip()
    led = led.lower().strip()
    
    # Xác thực status
    if status not in ["on", "off"]:
        status = "off"
    
    # Xác thực led
    if led not in ["1", "2", "all"]:
        led = "all"
    
    leds_to_control = []
    if led == "all":
        leds_to_control = ["1", "2"]
    else:
        leds_to_control = [led]
    
    led_statuses = {}
    error_message = ""
    
    for l in leds_to_control:
        url = f"https://{ESP8266_IP}/led{l}/{status}"
        led_status = None
        
        # Retry logic for each LED
        for attempt in range(MAX_RETRY):
            try:
                print(f"[light_control] Attempt {attempt + 1}/{MAX_RETRY}: Requesting {url}")
                response = requests.get(url, timeout=REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    response_text = response.text.strip()
                    print(f"[light_control] Response: {response_text}")
                    
                    # Parse response
                    lines = response_text.split('\n')
                    for line in lines:
                        if line.startswith(f'LED{l}='):
                            led_status = line.split('=')[1]
                            break
                    
                    break
                else:
                    error_message = f"HTTP {response.status_code}"
                    print(f"[light_control] HTTP Error: {error_message}")
                    
            except requests.exceptions.Timeout:
                error_message = f"Timeout sau {REQUEST_TIMEOUT}s (Attempt {attempt + 1}/{MAX_RETRY})"
                print(f"[light_control] {error_message}")
                
            except requests.exceptions.ConnectionError:
                error_message = f"Lỗi kết nối (Attempt {attempt + 1}/{MAX_RETRY}). Kiểm tra IP ESP8266: {ESP8266_IP}"
                print(f"[light_control] {error_message}")
                
            except Exception as e:
                error_message = f"Lỗi: {str(e)}"
                print(f"[light_control] {error_message}")
            
            # Wait before retry
            if attempt < MAX_RETRY - 1:
                time.sleep(1)
        
        led_statuses[l] = led_status
    
    # Generate response
    if all(led_statuses.values()):
        action_text = "bật" if status == "on" else "tắt"
        if led == "all":
            led_text = "tất cả đèn"
        else:
            led_text = f"đèn {led}"
        statuses_text = ", ".join([f"đèn {l}: {s}" for l, s in led_statuses.items()])
        response_content = f"Đã {action_text} {led_text} thành công. Trạng thái hiện tại: {statuses_text}."
    else:
        response_content = f"Xin lỗi, không thể {action_text} {led_text} do lỗi: {error_message}. Vui lòng kiểm tra ESP8266."
    
    return {
        "content": response_content,
        "image": []
    }