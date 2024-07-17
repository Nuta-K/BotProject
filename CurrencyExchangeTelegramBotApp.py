import telebot
from currency_converter import CurrencyConverter
from telebot import types
from config import TOKEN

bot = telebot.TeleBot(TOKEN)
currency = CurrencyConverter()
amount = 0


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hello! Please enter the amount')
    bot.register_next_step_handler(message, summa)


@bot.message_handler(content_types=['text'])
def summa(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid input format. Please try again.')
        bot.register_next_step_handler(message, summa)
        return

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        button1 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        button2 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        button3 = types.InlineKeyboardButton('USD/GBP', callback_data='usd/gbp')
        button4 = types.InlineKeyboardButton('GBP/USD', callback_data='gbp/usd')
        button5 = types.InlineKeyboardButton('Other currency', callback_data='else')
        markup.add(button1, button2, button3, button4, button5)
        bot.send_message(message.chat.id, 'Please, choose the currency', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'The amount should be more than zero. Try again')
        bot.register_next_step_handler(message, summa)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data != 'else':
        values = call.data.upper().split('/')
        result = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id,f'You get {round(result,2)} {values[1]}. Enter another amount or convert the current summa in different currency via buttons')
        bot.register_next_step_handler(call.message, summa)
    else:
        bot.send_message(call.message.chat.id, 'Please enter couple of currencies separated by "/"')
        bot.register_next_step_handler(call.message, my_currency)


@bot.callback_query_handler(func=lambda call: True)
def my_currency(message):
    try:
        values = message.text.upper().split('/')
        result = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f'You get {round(result, 2)} {values[1]}. Enter another amount')
        bot.register_next_step_handler(message, summa)
    except ValueError:
        bot.send_message(message.chat.id, 'One or both currency are not support. Enter another pair of currency')
        bot.register_next_step_handler(message, my_currency)
    except IndexError:
        bot.send_message(message.chat.id, 'One or both currencies are not supported. Enter another pair of currencies')
    except OverflowError:
        bot.send_message(message.chat.id, 'Invalid input format')
    except Exception as e:
        bot.send_message(message.chat.id,f'The selected currencies cannot be exchanged at this time. Tap on the '
                                         f'"Other currency" button to choose new pair of currencies')
        return


bot.polling(none_stop=True)
