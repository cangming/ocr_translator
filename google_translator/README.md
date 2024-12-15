Google OCR translator
===
It's use tesseract for OCR, then use google translator API

1. install python
2. pip install pyvenv
2. python -m venv venv
3. venv\Scripts\activate
4. pip install -r .\requirements.txt
5. install [tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
5. copy config.yaml.example to config.yaml
6. modify config.yaml and fill your setting
7. python google_translator.py
8. press "設定抓取範圍" then drag the screen range you want to auto capture
9. press "開始螢幕截圖" then the translate windows will show the screen capture now, you can press "設定抓取範圍" to reset screen capture any time
10. The OCR result will auto show in "原文" textbox and the translate result will auto update in "翻譯結果" textbox

If you want to use google_translator.zip in release, follow the steps
1. Install [tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Extract zip
3. Fill the config.yaml
4. Launch the google_translator.exe.