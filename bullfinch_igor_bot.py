#!/usr/bin/env python3

import time
import pygame
import pygame.camera
from telegram import ChatAction, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import configparser

class Photographer():

    def __init__(self, device, resolution, pic):
        self.device = device
        self.resolution = resolution
        self.pic = pic

    def start(self, bot, update):
        custom_keyboard = [["/now"]]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
        msg = "Добрый день, это бот снегиря Игоря.\n" \
              "Если вы хотите посмотреть, что сейчас делает Игорь, нажмите на кнопку внизу" \
              " или просто отправьте /now."
        bot.send_message(chat_id=update.message.chat_id,
                         text=msg, reply_markup=reply_markup)

    def send_photo(self, bot, update):
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)
        self.make_shot()
        photo = open(self.pic, 'rb')
        bot.sendPhoto(chat_id=update.message.chat_id, photo=photo)

    def make_shot(self):
        pygame.camera.init()
        cam = pygame.camera.Camera(self.device, 
                                   tuple(map(int, self.resolution.split('x'))))
        cam.start()
        time.sleep(3) # need to play with it
        img = cam.get_image()
        pygame.image.save(img, self.pic)
        cam.stop()


def read_config():

    config = configparser.ConfigParser()
    config.read('bullfinch_igor_bot.cfg')

    return (config['bot']['token'],
            config['camera']['device'],
            config['camera']['resolution'])


def main():

    token, device, resolution = read_config()

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    photographer = Photographer(device, resolution, "/tmp/igor.jpg")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", photographer.start))
    dp.add_handler(CommandHandler("now", photographer.send_photo))
    # dp.add_handler(CommandHandler("help", hetakelp))
    # dp.add_handler(CommandHandler("tell", tell_weather))
    # dp.add_handler(CommandHandler("kitty", send_kitty))

    # log all errors
    # dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
