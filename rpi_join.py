import time
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from threading import Thread

print("-"*200)

def start_virtual_display():
    print("-"*200)
    display = Display(visible=0, size=(1600, 1200))
    display.start()

def browse_room(room_name):
    options = webdriver.ChromeOptions()
    # allow access to camera device
    options.add_argument("--use-fake-ui-for-media-stream")

    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=options)


    driver.get("http://localhost:5000")

    driver.implicitly_wait(0.5)

    text_box = driver.find_element(by=By.NAME, value="room_name")
    submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")

    text_box.send_keys(room_name)
    submit_button.click()

    print("Submit button")
    return driver


class RpiJoinThread(Thread):

    def __init__(self, room_name, event):
        super(RpiJoinThread, self).__init__()
        self.room_name = room_name
        self.event = event

    def run(self):
        start_virtual_display()
        driver = browse_room(self.room_name)
        while True:
            for log in driver.get_log('browser'):
                print(log)
            if self.event.is_set():
                break
            time.sleep(2)

