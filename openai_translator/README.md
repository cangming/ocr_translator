OpenAI OCR translator
===
Notice: The OpenAI billing can be surprising, so pay attention to the frequency of pressing the translation button and set a limit on your OpenAI account in advance to ensure the amount remains affordable.

1. install python
2. pip install pyvenv
2. python -m venv venv
3. venv\Scripts\activate
4. pip install -r .\requirements.txt
5. copy config.yaml.example to config.yaml
6. modify config.yaml and fill your setting
7. python openai_translator.py
8. press "設定抓取範圍" then drag the screen range you want to auto capture
9. press "開始螢幕截圖" then the translate windows will show the screen capture now, you can press "設定抓取範圍" to reset screen capture any time
10. press "翻譯", then openai result will be show in "翻譯結果" textbox. You can scroll mouse if output is too large.

If you want to use openai_translator.zip in release, follow the steps
1. extract zip
2. Fill the config.yaml
3. Launch the openai_translator.exe.