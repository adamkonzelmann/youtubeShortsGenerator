from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import requests
import json

import time

driver = webdriver.Firefox()
driver.get("https://www.reddit.com/r/AmItheAsshole/top/?t=all")

time.sleep(3)

SCROLL_PAUSE_TIME = 2

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

for x in range(0,20):
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")

    last_height = new_height

posts = driver.find_elements(By.XPATH, "//div[@style='--emote-size: 20px']")
urls = []

for post in posts:
    postURL = post.find_element(By.XPATH, "..")
    unformattedURL = str(postURL.get_attribute('href'))
    useURL = unformattedURL[:-1] + ".json"

    urls.append(useURL)

print(urls)

driver.close()

folderName = "posts"
maxRetries = 10
for count, url in enumerate(urls):
    if url != 'Non.json':
        retryCount = 0
        while retryCount < maxRetries:
            time.sleep(10)
            response = requests.get(url)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                text = json_data[0]["data"]["children"][0]["data"]["selftext"]
                title = json_data[0]["data"]["children"][0]["data"]["title"]
                print(count + ": " + title)

                filePath = f'{folderName}/post{count}.txt'
                with open(filePath, 'w') as file:
                    file.write(title + "\n" + text)
                retryCount = 10
            else:
                print(f"Failed to retrieve data. Status code: {response.status_code}")
            retryCount += 1
