# this part gets the reviews for the film that is an input for an app and that is an output using webscrapping of IMDb

#!pip install selenium
#!apt install chromium-chromedriver
# !pip install fake-useragent

import time
from selenium import webdriver
from selenium.webdriver.common.by import By #needed for selecting the elements of the webpage
from fake_useragent import UserAgent

def webscrap_rating(IMDb_ID):
    ua = UserAgent()
    userAgent = ua.random
    #print(userAgent)

    url = 'https://www.imdb.com/title/' + IMDb_ID +'/ratings/'

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'user-agent={userAgent}')
    wd = webdriver.Chrome(options=chrome_options)

    try:
        wd.get(url)
    except:
        print("Some issue encountered while trying to read the webpage. Restarting the webdriver and trying again.")
        wd = webdriver.Chrome(options=chrome_options)
        wd.get(url)

    time.sleep(5) # Wait for webpage to load

    #wd.save_screenshot("screenshot.png")
    rating = wd.find_element(By.XPATH, ("//span[@class='sc-5931bdee-1 gVydpF']"))
    rating = rating.text

    wd.quit()
    return(rating)

example = webscrap_rating(IMDb_ID = 'tt1517268') #'tt1375666' #
print(example)