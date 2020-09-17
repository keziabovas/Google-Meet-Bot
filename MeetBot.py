
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import schedule
import time
import requests

geckopath = ""  #Path to GeckoDriver on your computer

gmailId = ""  #Your Mail ID preferably Organisational Mail ID
passWord = "" #You Password

dur = ""  #Duration of the Meeting in Minutes

def telegram_bot_sendtext(bot_message):
    
    bot_token = '' #Your Bot Token
    bot_chatID = '' #Your ChatID
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

participants = 10
init_participants = 0
options = FirefoxOptions()
options.set_preference("permissions.default.microphone", 2)
options.set_preference("permissions.default.camera", 2)
driver = webdriver.Firefox(options=options,executable_path=geckopath)


def switch_focus():
    Window_List = driver.window_handles
    driver.switch_to_window(Window_List[-1])

def leave():
    init_participants = int(driver.find_element_by_xpath("/html/body/div[1]/c-wiz/div[1]/div/div[5]/div[3]/div[6]/div[3]/div/div[2]/div[1]/span/span/div/div/span[2]").text)
    print("initial participants =" + str(init_participants))
    i = 0
    while True:
        i+=1
        participants = int(driver.find_element_by_xpath("/html/body/div[1]/c-wiz/div[1]/div/div[5]/div[3]/div[6]/div[3]/div/div[2]/div[1]/span/span/div/div/span[2]").text)
        print(str(init_participants - participants))
        if (init_participants - participants >= 15 or i == ((dur*60)/5)): 
            driver.close()
            switch_focus()
            break
        time.sleep(5)
        

def start_bot():
    driver.get("https://www.gmail.com") 

    email_field = driver.find_element_by_name('identifier')
    email_field.send_keys(gmailId)
    email_field.send_keys(Keys.ENTER)
    time.sleep(3)

    password_field = driver.find_element_by_name("password")
    password_field.send_keys(passWord)
    password_field.send_keys(Keys.ENTER)
    time.sleep(6)

def biomed():
    driver.execute_script("window.open('');")
    switch_focus()
    driver.get(" ") #Meeting Link
    time.sleep(3)
    driver.find_element_by_xpath("/html/body/div[1]/c-wiz/div/div/div[5]/div[3]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div[1]").click()
    telegram_bot_sendtext("BioMed Class Starts")
    time.sleep((dur/2)*60)
    leave()
    telegram_bot_sendtext("BioMed Class Ends")


start_bot()
schedule.every().wednesday.at("08:30").do(biomed) #Schedule according to your Need

while True:
    schedule.run_pending()
    time.sleep(1)







