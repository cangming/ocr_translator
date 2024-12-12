import mss
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
import pyautogui

class ScreenCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("螢幕截圖顯示")
        
        self.is_capturing = False  # 控制捕捉狀態
        self.capture_interval = 1000  # 截圖間隔，毫秒

        # 創建輸入欄位標籤和輸入框
        tk.Label(root, text="起始座標:").grid(row=0, column=0)
        self.entry_x = tk.Entry(root)
        self.entry_x.grid(row=0, column=1)

        self.entry_y = tk.Entry(root)
        self.entry_y.grid(row=0, column=2)

        tk.Label(root, text="寬/高:").grid(row=1, column=0)
        self.entry_width = tk.Entry(root)
        self.entry_width.grid(row=1, column=1)

        self.entry_height = tk.Entry(root)
        self.entry_height.grid(row=1, column=2)

        tk.Label(root, text="螢幕編號:").grid(row=2, column=0)
        self.entry_monitor = tk.Entry(root)
        self.entry_monitor.grid(row=2, column=1)

        # 添加顯示滑鼠座標的欄位
        tk.Label(root, text="滑鼠座標:").grid(row=3, column=0)
        self.mouse_x = tk.StringVar()
        tk.Entry(root, textvariable=self.mouse_x, state='readonly').grid(row=3, column=1)

        self.mouse_y = tk.StringVar()
        tk.Entry(root, textvariable=self.mouse_y, state='readonly').grid(row=3, column=2)

        tk.Label(root, text="所屬螢幕編號:").grid(row=4, column=0)
        self.screen_id = tk.StringVar()
        tk.Entry(root, textvariable=self.screen_id, state='readonly').grid(row=4, column=1)

        # 添加截圖按鈕
        self.capture_button = tk.Button(root, text="開始螢幕截圖", command=self.toggle_capture)
        self.capture_button.grid(row=5, column=0, columnspan=2)

        # 添加一個標籤來顯示圖片
        self.label_image = tk.Label(root)
        self.label_image.grid(row=9, column=0, columnspan=2)

        # 更新滑鼠座標的函式
        self.update_mouse_coordinates()

    def toggle_capture(self):
        # 切換捕捉狀態
        self.is_capturing = not self.is_capturing
        if self.is_capturing:
            self.capture_button.config(text="停止螢幕截圖")
            self.start_capturing()
        else:
            self.capture_button.config(text="開始螢幕截圖")

    def start_capturing(self):
        # 獲取捕捉設定值
        try:
            x = int(self.entry_x.get())
            y = int(self.entry_y.get())
            width = int(self.entry_width.get())
            height = int(self.entry_height.get())
            monitor_id = int(self.entry_monitor.get())

            with mss.mss() as sct:
                if monitor_id < 1 or monitor_id >= len(sct.monitors):
                    raise ValueError("螢幕編號無效")

                self.monitor = sct.monitors[monitor_id]

                self.capture_screenshot(x, y, width, height)

        except ValueError as e:
            messagebox.showerror("錯誤", str(e))

    def capture_screenshot(self, x, y, width, height):
        # 定義擷取的邊界框
        left = self.monitor["left"] + x
        top = self.monitor["top"] + y
        right = left + width
        lower = top + height
        bbox = (left, top, right, lower)

        # 擷取圖片
        with mss.mss() as sct:
            im = sct.grab(bbox)
            img = Image.frombytes("RGB", im.size, im.rgb)
            img_tk = ImageTk.PhotoImage(img)

            # 在視窗中顯示圖片
            self.label_image.config(image=img_tk)
            self.label_image.image = img_tk  # 保存圖片的引用，避免垃圾收集

            if self.is_capturing:  # 如果仍在捕捉中，繼續定時擷取
                self.root.after(self.capture_interval, self.capture_screenshot, x, y, width, height)

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

# 創建 tkinter 視窗並運行主循環
root = tk.Tk()
app = ScreenCaptureApp(root)
root.mainloop()