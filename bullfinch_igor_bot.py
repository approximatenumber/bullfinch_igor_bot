#!/usr/bin/env python3

import time
import pygame
import pygame.camera
from telegram import ChatAction, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler
import configparser


class Photographer():

    def __init__(self, device, resolution, pic):
        self.device = device
        self.resolution = resolution
        self.pic = pic
        self.photo_count = 0
        self.lastday = ""

    def recalculate_photo_count(self):

        current_time = time.localtime()
        today = current_time.tm_mday

        if self.lastday:

            if today > self.lastday:
                print("%s: now is a new day, \
                       resetting the count..." % time.asctime())
                self.lastday = today
                self.photo_count = 0

            else:
                print("%s: now is not a new day" % time.asctime())
                self.photo_count += 1

        else:
            print("%s: script started, so lastday is today" % time.asctime())
            self.lastday = today
            self.photo_count += 1

        print(self.photo_count)

    def start(self, bot, update):

        custom_keyboard = [["/now"]]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
        msg = "Добрый день, это бот снегиря Игоря.\n" \
              "Если вы хотите посмотреть, что сейчас делает Игорь, нажмите на кнопку внизу " \
              "или просто отправьте /now."
        bot.send_message(chat_id=update.message.chat_id,
                         text=msg, reply_markup=reply_markup)

    def send_photo(self, bot, update):

        def make_shot():
            pygame.camera.init()
            cam = pygame.camera.Camera(self.device,
                                       tuple(map(int,
                                                 self.resolution.split('x'))))
            cam.start()
            time.sleep(3)  # need to play with it
            img = cam.get_image()
            pygame.image.save(img, self.pic)
            cam.stop()

        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.UPLOAD_PHOTO)

        make_shot()
        photo = open(self.pic, 'rb')
        bot.sendPhoto(chat_id=update.message.chat_id, photo=photo)
        self.recalculate_photo_count()

    def send_statistic(self, bot, update):

        message = "За сегодняшний день Игоря хотели увидеть " \
                  "столько раз: %d" % self.photo_count
        bot.send_message(chat_id=update.message.chat_id, text="За сегодняшний день Игоря хотели увидеть " \
                                                              "столько раз: %d" % self.photo_count)


def read_config(config_file):

    config = configparser.ConfigParser()
    config.read(config_file)

    return {'token':       config['bot']['token'],
            'device':      config['camera']['device'],
            'resolution':  config['camera']['resolution']}


def main():

    config = read_config('bullfinch_igor_bot.cfg')

    token = config['token']
    device = config['device']
    resolution = config['resolution']

    pic = '/tmp/igor/igor.jpg'

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    photographer = Photographer(device, resolution, pic)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", photographer.start))
    dp.add_handler(CommandHandler("now", photographer.send_photo))
    dp.add_handler(CommandHandler("stat", photographer.send_statistic))

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
