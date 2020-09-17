import logging
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import schedule
import time
import requests


from telegram import ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

path = " " #GeckoPath
gmailId = "@ceconline.edu" #MailID
passWord = "" #Password
bot_token = '' #Bot Token
bot_chatID = '' #ChatID


participants = 10
init_participants = 0
options = FirefoxOptions()
options.set_preference("permissions.default.microphone", 2)
options.set_preference("permissions.default.camera", 2)
driver = webdriver.Firefox(options=options,executable_path=path)



def telegram_bot_sendtext(bot_message):
    
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def switch_focus():
    Window_List = driver.window_handles
    driver.switch_to_window(Window_List[-1])

def leave(dur):
    init_participants = int(driver.find_element_by_xpath("/html/body/div[1]/c-wiz/div[1]/div/div[5]/div[3]/div[6]/div[3]/div/div[2]/div[1]/span/span/div/div/span[2]").text)
    print("initial participants =" + str(init_participants))
    i = 0
    while True:
        i+=1
        participants = int(driver.find_element_by_xpath("/html/body/div[1]/c-wiz/div[1]/div/div[5]/div[3]/div[6]/div[3]/div/div[2]/div[1]/span/span/div/div/span[2]").text)
        print(str(init_participants - participants))
        if (init_participants - participants >= 15 or i == (((dur+15)*60)/5)):
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

def meet(link,dur):
    driver.execute_script("window.open('');")
    switch_focus()
    driver.get(link)
    time.sleep(20)
    driver.find_element_by_xpath("/html/body/div[1]/c-wiz/div/div/div[5]/div[3]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div[1]").click()
    telegram_bot_sendtext("Class Thodangi " + link)
    time.sleep((dur/2)*60)   
    leave(dur)
    telegram_bot_sendtext("Class Theernu")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['Meet Link', 'Duration'],
                  ['Done']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data):

    facts = list()
    for key, value in user_data.items():
        facts.append(value)

    return "\n".join(facts).join(['\n', '\n'])

def facts_to(user_data):
    
    facts = list()
    for key, value in user_data.items():
        facts.append(value)

    return facts


def start(update, context):
    update.message.reply_text(
        "Hi! My name is Doctor Meet, I'll help you attend your Google Meet",
        reply_markup=markup)

    return CHOOSING


def regular_choice(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        'Your {}? Yes, I would love to hear about that!'.format(text.lower()))

    return TYPING_REPLY




def received_information(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text("Neat! Just so you know, this is what you already told me:"
                              "{} You can tell me more, or change your opinion"
                              " on something.".format(facts_to_str(user_data)),
                              reply_markup=markup)

    return CHOOSING


def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("Sit Back! Your Meeting has been started, you will be updated when the meeting ends.")
    link = (facts_to(user_data)[0])
    dur = int(facts_to(user_data)[1])
    start_bot()
    meet(link,dur)
    user_data.clear()
    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(bot_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Meet Link|Duration)$'),
                                      regular_choice)
                       ],

            TYPING_CHOICE: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                               regular_choice)],

            TYPING_REPLY: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                               received_information)],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    )

    dp.add_handler(conv_handler)


    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
