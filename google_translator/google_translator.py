import mss
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
import pyautogui
import pytesseract
from pynput import mouse
from googletrans import Translator
import yaml
import argparse

class ScreenCaptureApp:
    def __init__(self, root, debug=False):
        self.translator = Translator()

        self.config = yaml.safe_load(open("config.yaml"))
        pytesseract.pytesseract.tesseract_cmd = self.config["tesseract"]["cmd"]

        self.root = root
        self.root.title("螢幕截圖顯示")
        
        self.is_capturing = False  # 控制捕捉狀態
        self.capture_interval = 1000  # 截圖間隔，毫秒
        self.last_captured_text = ""  # 儲存上一次捕獲的文本

        self.set_coordinates = False  # 控制是否設定座標

        self.set_hide_capture = False

        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()

        self.entry_x = tk.StringVar()
        self.entry_y = tk.StringVar()

        self.entry_width = tk.StringVar()
        self.entry_height = tk.StringVar()

        self.entry_monitor = tk.StringVar()

        self.mouse_x = tk.StringVar()
        self.mouse_y = tk.StringVar()

        self.screen_id = tk.StringVar()

        if debug:
            tk.Label(root, text="起始座標:").grid(row=0, column=0)
            tk.Entry(root, textvariable=self.entry_x, state='readonly').grid(row=0, column=1)
            tk.Entry(root, textvariable=self.entry_y, state='readonly').grid(row=0, column=2)

            tk.Label(root, text="寬/高:").grid(row=1, column=0)
            tk.Entry(root, textvariable=self.entry_width, state='readonly').grid(row=1, column=1)
            tk.Entry(root, textvariable=self.entry_height, state='readonly').grid(row=1, column=2)

            tk.Label(root, text="螢幕編號:").grid(row=2, column=0)
            tk.Entry(root, textvariable=self.entry_monitor, state='readonly').grid(row=2, column=1)

            tk.Label(root, text="滑鼠座標:").grid(row=3, column=0)
            tk.Entry(root, textvariable=self.mouse_x, state='readonly').grid(row=3, column=1)
            tk.Entry(root, textvariable=self.mouse_y, state='readonly').grid(row=3, column=2)

            tk.Label(root, text="所屬螢幕編號:").grid(row=4, column=0)
            tk.Entry(root, textvariable=self.screen_id, state='readonly').grid(row=4, column=1)

        # 添加設定範圍按鈕
        self.set_coordinate_button = tk.Button(root, text="設定抓取範圍", command=self.toggle_set_coordinates)
        self.set_coordinate_button.grid(row=5, column=0)

        # 添加截圖按鈕
        self.capture_button = tk.Button(root, text="開始螢幕截圖", command=self.toggle_capture)
        self.capture_button.grid(row=5, column=1)

        # 翻譯按鈕
        self.hide_capture_button = tk.Button(root, text="隱藏截圖畫面", command=self.toggle_hide_capture)
        self.hide_capture_button.grid(row=5, column=2)

        # 添加顯示OCR標籤
        tk.Label(root, text="原文:").grid(row=6, column=0, columnspan=4)
        self.original_text = tk.Text(root, wrap='word', height=5)
        self.original_text.grid(row=7, column=0, columnspan=4, sticky='ew')

        # 添加顯示翻譯結果的標籤
        tk.Label(root, text="翻譯結果:").grid(row=6, column=4, columnspan=4)
        self.translated_text = tk.Text(root, wrap='word', height=5)
        self.translated_text.grid(row=7, column=4, columnspan=4, sticky='ew')

        # 添加一個標籤來顯示圖片
        self.label_image = tk.Label(root)
        self.label_image.grid(row=8, column=0, columnspan=5)

        root.grid_columnconfigure(3, weight=1)
        root.grid_columnconfigure(4, weight=1)

        # 更新滑鼠座標的函式
        self.update_mouse_coordinates()
    
    # destructor
    def __del__(self):
        self.listener.stop()
        self.listener.join()

    def on_click(self, x, y, button, pressed):
        if not self.set_coordinates:
            return

        if pressed:
            self.entry_x.set(self.mouse_x.get())
            self.entry_y.set(self.mouse_y.get())
            self.entry_monitor.set(self.screen_id.get())
        else:
            now_x = int(self.mouse_x.get())
            now_y = int(self.mouse_y.get())
            if int(self.entry_x.get()) < now_x:
                self.entry_width.set(now_x - int(self.entry_x.get()))
            else:
                self.entry_width.set(int(self.entry_x.get()) - now_x)
                self.entry_x.set(now_x)
            
            if int(self.entry_y.get()) < now_y:
                self.entry_height.set(now_y - int(self.entry_y.get()))
            else:
                self.entry_height.set(int(self.entry_y.get()) - now_y)
                self.entry_y.set(now_y)

            self.set_coordinates = False
            self.set_coordinate_button.config(text="設定抓取範圍")

    def toggle_set_coordinates(self):
        self.set_coordinates = True
        self.set_coordinate_button.config(text="設定抓取範圍中")

    def toggle_capture(self):
        # 切換捕捉狀態
        self.is_capturing = not self.is_capturing
        if self.is_capturing:
            self.capture_button.config(text="停止螢幕截圖")
            self.start_capturing()
        else:
            self.capture_button.config(text="開始螢幕截圖")
    
    def toggle_hide_capture(self):
        self.set_hide_capture = not self.set_hide_capture
        if self.set_hide_capture:
            self.hide_capture_button.config(text="顯示截圖畫面")
            self.label_image.grid_forget()
        else:
            self.hide_capture_button.config(text="隱藏截圖畫面")
            self.label_image.grid(row=8, column=0, columnspan=5)

    def start_capturing(self):
        # 獲取捕捉設定值
        try:
            self.capture_screenshot()

        except ValueError as e:
            messagebox.showerror("錯誤", str(e))

    def capture_screenshot(self):
        x = int(self.entry_x.get())
        y = int(self.entry_y.get())
        width = int(self.entry_width.get())
        height = int(self.entry_height.get())

        # 定義擷取的邊界框
        left = x
        top = y
        right = left + width
        lower = top + height
        bbox = (left, top, right, lower)

        # 擷取圖片
        with mss.mss() as sct:
            im = sct.grab(bbox)
            img = Image.frombytes("RGB", im.size, im.rgb)

            # 使用 pytesseract 進行文字識別
            text = pytesseract.image_to_string(img, lang=self.config["tesseract"]["ocr_language"]).strip()  # 日文

            # 比對截圖文本是否有變動
            if text != self.last_captured_text:
                self.last_captured_text = text  # 更新為最新的文字

                self.original_text.delete(1.0, tk.END)
                self.original_text.insert(tk.END, text)
                translated = self.translate_text(text)  # 翻譯文本
                self.translated_text.delete(1.0, tk.END)
                self.translated_text.insert(tk.END, translated) # 更新翻譯結果

            img_tk = ImageTk.PhotoImage(img)
            # 在視窗中顯示圖片
            self.label_image.config(image=img_tk)
            self.label_image.image = img_tk  # 保存圖片的引用，避免垃圾收集

            if self.is_capturing:  # 如果仍在捕捉中，繼續定時擷取
                self.root.after(self.capture_interval, self.capture_screenshot)

    def translate_text(self, text):
        # 這邊用 requests 對 Google 翻譯 API 發送請求，記得換成你的 API 金鑰
        try:
            return self.translator.translate(text.replace('\n', ''), dest=self.config["google"]["target_language"]).text
        except Exception as e:
            return f"翻譯錯誤: {str(e)}"

    def update_mouse_position(self):
        # 獲取滑鼠當前位置
        x, y = pyautogui.position()
        self.mouse_x.set(x)
        self.mouse_y.set(y)

        # 獲取滑鼠所在的螢幕編號
        with mss.mss() as sct:
            for i in range(1, len(sct.monitors)):
                monitor = sct.monitors[i]
                if monitor["left"] <= x <= monitor["left"] + monitor["width"] and monitor["top"] <= y <= monitor["top"] + monitor["height"]:
                    self.screen_id.set(i)
                    break

    def update_mouse_coordinates(self):
        self.update_mouse_position()
        self.root.after(100, self.update_mouse_coordinates)  # 每 100 毫秒更新一次

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Google Translator with Screen Capture')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
args = parser.parse_args()

# 創建 tkinter 視窗並運行主循環
root = tk.Tk()
root.attributes('-topmost', True)
app = ScreenCaptureApp(root, debug=args.debug)
root.mainloop()