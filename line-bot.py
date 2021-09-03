from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

# scraping
from selenium import webdriver
from webdriver_manager import chrome
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = scraping()
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text + text))

def scraping():
    NUMBER = "0015081677"
    PASSWORD = "20050102s"

    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.use_chromium = True
    options.add_argument('--disable-gpu');
    options.add_argument('--disable-extensions');
    options.add_argument('--proxy-server="direct://"');
    options.add_argument('--proxy-bypass-list=*');
    options.add_argument('--start-maximized');
    options.add_argument('--headless');

    browser = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), chrome_options=options)

    url = "https://v-yoyaku.jp/282014-himeji"
    browser.get(url)
    browser.implicitly_wait(3)

    # print("ログインページにアクセスしました")

    # 入力
    e = browser.find_element_by_id("login_id")
    e.clear()
    e.send_keys(NUMBER)

    e = browser.find_element_by_id("login_pwd")
    e.clear()
    e.send_keys(PASSWORD)

    # フォームを転送
    # print("テスト")
    element = browser.find_element_by_id("btn_login")
    browser.execute_script("arguments[0].click();", element)
    # print("情報を入力してログインボタンを押しました")

    browser.implicitly_wait(3)

    mypage_url = browser.find_element_by_css_selector(".btn-primary")
    mypage_url = mypage_url.get_attribute("href")
    browser.get(mypage_url)
    # print("マイページのURL: ", mypage_url)

    browser.implicitly_wait(3)

    element = browser.find_element_by_id("btn_Search_Medical")
    browser.execute_script("arguments[0].click();", element)
    # print("接種会場を選択")

    browser.implicitly_wait(3)

    element = browser.find_element_by_id("btn_search_medical")
    browser.execute_script("arguments[0].click();", element)
    # print("検索")

    browser.implicitly_wait(20)
    time.sleep(2)

    element = browser.find_element_by_id("count_all")
    # print(element.get_attribute("textContent"))
    # print(element.text)

    # print(element.get_attribute("textContent"))
    browser.quit()
    return element.text


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)