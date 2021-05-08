import telegram
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
)
from telegram.ext import (
    Updater,
    handler,
    Filters,
    CallbackContext,
    MessageHandler,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
)
from config import BOT_TOKEN
from datetime import datetime
from check_resi import check_resi

FIRST, SELECT_EXPEDITIONS, INPUT_RESI = map(chr, range(3))
JNE, JNT, POS, LION, NINJA, SICEPAT, TIKI, ANTERAJA, WAHANA = map(
    chr, range(3, 12))
END = ConversationHandler.END


class TelegramBot:

    def __init__(self):
        self.bot = telegram.Bot(token=BOT_TOKEN)
        self.updater = Updater(token=BOT_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.updater.start_polling()
        self.add_menu()

    def add_menu(self):
        self.select_expedition = {}
        self.expeditions = [
            'JNE',
            'JNT',
            'Pos',
            'Lion',
            'Ninja',
            'SiCepat',
            'TIKI',
            'Anteraja',
            'Wahana',
        ]

        select_action = [
        ]

        for expedition in self.expeditions:
            select_action.append(
                CallbackQueryHandler(
                    self.get_resi,
                    pattern='^' + expedition.upper() + '$',
                    pass_chat_data=True
                ),
            )

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                FIRST: [CommandHandler('start', self.start)],
                SELECT_EXPEDITIONS: select_action,
                INPUT_RESI: [
                    MessageHandler(
                        Filters.text,
                        self.get_data,
                    )
                ]
            },
            fallbacks=[CommandHandler('stop', self.stop)],
        )
        self.dispatcher.add_handler(conv_handler)

    def start(self, update: Update, context: CallbackContext):
        self.setKeyboardMenu(update.effective_chat.id)

        if context.user_data.get(FIRST):
            update.callback_query.answer()
            update.callback_query.edit_message_text(
                text="Silahkan pilih Ekspedisi :", reply_markup=self.keyboard)
        else:
            update.message.reply_text(
                text="Silahkan pilih Ekspedisi :", reply_markup=self.keyboard)

        return SELECT_EXPEDITIONS

    def stop(self, update: Update, context: CallbackContext):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text="Zeeb Mang")

        return END

    def get_resi(self, update: Update, context: CallbackContext):
        self.select_expedition[update.effective_chat.id] = update.callback_query.data
        update.callback_query.answer()
        update.callback_query.edit_message_text(text="Masukan Resi :")

        return INPUT_RESI

    def get_data(self, update: Update, context: CallbackContext):
        resi = update._effective_message.text
        expedition = self.select_expedition[update.effective_chat.id]
        text="Memeriksa resi {} dari ekspedisi {}".format(resi, expedition)

        self.send_message(update.effective_chat.id, text)
        self.send_message(update.effective_chat.id, 'Mohon tunggu...')

        if (expedition == 'POS'):
            self.send_message(update.effective_chat.id, 'Mohon maaf terjadi kendala menghubungi kurir, harap coba beberapa saat lagi')
            return END

        # Do Request to API
        result = check_resi(expedition.lower(), resi)

        if 'error' in result:
            self.send_message(update.effective_chat.id, result['message'])
        else:
            historys = result['data']['detail']['history']
            historys.reverse()
            
            message = ""
            for history in historys:
                message = message+"*{}*\n{}\n\n".format(history['time'], history['desc'])
            
            self.send_message(update.effective_chat.id, message)

        return END

    # Send message to all notified user
    def send_message(self, chat_id, message):
        # Split a message every 4096 chars (The maximum length of sending messages on Telegram)
        msgs = [message[i:i + 4096] for i in range(0, len(message), 4096)]

        for text in msgs:
            try:
                self.bot.send_message(chat_id=chat_id, text=text, parse_mode='markdown'), "Send Message"
            except Exception as e:
                print("{} : {}".format(chat_id, str(e)))

    def setKeyboardMenu(self, userId):
        buttons = [
        ]

        for i in range(0, len(self.expeditions), 3):
            expedition1 = self.expeditions[i]
            expedition2 = self.expeditions[i+1]
            expedition3 = self.expeditions[i+2]
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=expedition1,
                        callback_data=expedition1.upper(),
                    ),
                    InlineKeyboardButton(
                        text=expedition2,
                        callback_data=expedition2.upper(),
                    ),
                    InlineKeyboardButton(
                        text=expedition3,
                        callback_data=expedition3.upper(),
                    ),
                ]
            )

        self.keyboard = InlineKeyboardMarkup(buttons)
