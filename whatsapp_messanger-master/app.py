from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        group_ids = request.form['group_id'].split(',')  
        message = request.form['message']

        try:
            send_whatsapp_message(group_ids, message)  
            return "WhatsApp messages sent successfully."
        except Exception as e:
            return f"An exception occurred while sending the WhatsApp messages: {str(e)}"

    return render_template('index.html')


def send_whatsapp_message(group_ids, message):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Run Chrome in headless mode (without GUI)
    # options.add_argument('--disable-gpu')  # Disable GPU acceleration for headless mode

    with webdriver.Chrome(options=options) as driver:
        for group_id in group_ids:
            open_group_chat(driver, group_id)
            wait_for_chat_input(driver)
            send_message(driver, message)
            wait_for_message_sent(driver)  

def open_group_chat(driver, group_id):
    group_url = f'https://web.whatsapp.com/accept?code={group_id}'
    driver.execute_script("window.open('', '_blank');")
    driver.switch_to.window(driver.window_handles[-1]) 
    driver.get(group_url)


def wait_for_chat_input(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
    )


def send_message(driver, message):
    chat_input = driver.find_element_by_xpath("//div[@contenteditable='true']")
    chat_input.send_keys(message)
    chat_input.send_keys(Keys.RETURN)


def wait_for_message_sent(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'message-out') and .//*[contains(@data-icon, 'check')]]"))
    )


if __name__ == '__main__':
    app.run()
