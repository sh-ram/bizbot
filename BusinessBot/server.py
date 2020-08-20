import logging
import os

from telegram import ( ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                       ParseMode )
from telegram.ext import ( CallbackContext, CommandHandler, ConversationHandler,
                           Filters, MessageHandler, Updater )
from telegram.ext.dispatcher import run_async
from telegram.ext.jobqueue import Days

import BotResponse
import BotModel
import jobs
import time_
from BotModel import BotWebModel
from currencies import Currencies
from jobs import Id, Job
from MessageFilters import Patterns, ReFilter, Regex

# Conversation states
RATE, NOTIFY, TIME = range(3)
CONVERSATION = { '/rate':RATE, '/notify':NOTIFY }

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

@run_async
def start(update, context):
    '''Show bot equipment commands set.'''
    name, description = range(2)
    text = 'Бот умеет:\n'
    for command in BotModel.BOT_COMMANDS:
        text += f'/{command[name]} {command[description]}\n'
    update.message.reply_text(text=text,
                              parse_mode=ParseMode.HTML,
                              disable_notification=True)

def notify_force(update, context):
    ''' 
        Add job if message contain 'command', 'currency' and 'time'.
        E.g.: "/notifyeur15:10:01","/notify eur 15:10", etc.
    '''
    regex = Regex()
    currency = regex.match(Patterns.CURRENCY, update.message.text)
    time = regex.match(Patterns.TIME_CONV, update.message.text)
    currency_index = Currencies().get_index(currency)
    time = time_.get_msk(time)
    text = ''
    if not currency_index:
        text = BotResponse.currency_invalid(update.message.text)
    elif not time:
        text = BotResponse.time_invalid
    else:
        queue = context.job_queue
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id
        queue.run_daily(callback=callback_rate,
                        time=time, 
                        days=Days.EVERY_DAY, 
                        context=chat_id, 
                        name=jobs.get_job_name(currency_index))
        time = time.strftime(jobs.TIME_FORMAT)
        days = ''.join( [str(x) for x in tuple(Days.EVERY_DAY)] ) 
        
        job = Job( currency_index, time, days=days, id=Id(chat_id, user_id) )  
        jobs.disable_job(queue, chat_id, currency_index)
        jobs.add_job(job)
        text = BotResponse.job_stated(currency_index, time)
    update.message.reply_text(text, parse_mode=ParseMode.HTML)
  
@run_async
def notifications(update, context):
    '''Show all active jobs.'''
    job_queue = jobs.get_job_queue_by_chat(update.message.chat_id)
    text = BotResponse.notifications(job_queue)
    update.message.reply_text(text, parse_mode=ParseMode.HTML)

@run_async
def disable(update, context):
    '''Remove job or all jobs from job_queue and set 'disable' to db job status.'''
    currency_index = context.match[0]
    chat_id = update.message.chat_id
    text = BotResponse.jobs_disabled if not currency_index else \
           BotResponse.job_disabled(currency_index)
    
    jobs.disable_job(queue=context.job_queue, 
                     chat_id=chat_id,
                     currency_index=currency_index)
    logger.info(f'User {update.message.from_user.first_name} disable notification.')
    update.message.reply_text(text, parse_mode=ParseMode.HTML)

@run_async
def conv_currency(update, context):
    '''Show keyboard with currency name values with mark roll.'''
    chat_data = context.chat_data
    user_data = context.user_data
    currencies = Currencies().get_currencies_names()
    if not 'mark' in user_data.keys(): user_data['mark'] = 0
    reply_keyboard = BotModel.get_keyboard(currencies, user_data['mark'])
    user_data['mark'] = reply_keyboard.mark
    reply_keyboard.rows.append('Отмена Еще'.split())
    text = BotResponse.conv_currency
    markup = ReplyKeyboardMarkup(reply_keyboard.rows, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(text=text, 
                              parse_mode=ParseMode.HTML,
                              reply_markup=markup)
    CONV = None
    message = update.message.text
    is_more = Regex().is_match(Patterns.CURRENCY_SHOW_MORE, message)
    if 'conv' in chat_data.keys(): 
        CONV = chat_data['conv']
    elif not is_more: 
        CONV = CONVERSATION[message]
    print(f'{CONV=}')
    return CONV

@run_async
def notify(update, context):
    '''
        Function is invoked after call "/notify" command when user already typed "currency" value,
        Parse any value e.g. [currency index] or [currency name].
        Shortcut: "/notifyUSD", "/notify Euro", etc.
    '''
    user_currency = Regex().match(Patterns.CURRENCY, update.message.text)
    currency_index = Currencies().get_index(user_currency)
    if currency_index:
        text = BotResponse.conv_time
        context.user_data['currency_index'] = currency_index
        update.message.reply_text(text, 
                                  parse_mode=ParseMode.HTML,
                                  reply_markup=ReplyKeyboardRemove())
        return TIME
    text = BotResponse.conv_currency_invalid(update.message.text)
    update.message.reply_text(text, parse_mode=ParseMode.HTML)
    context.chat_data['conv'] = NOTIFY
    return NOTIFY

@run_async
def time(update, context):
    ''' 
        Parse input user time. 
        Decline input if time is invalid then request user time again.
        Set job by UserJob tuple of data.
    '''
    queue = context.job_queue
    chat_id = update.message.chat_id
    user_id = update.effective_user.id
    time = Regex().match(Patterns.TIME_CONV, update.message.text)
    if not time: 
        text = BotResponse.conv_time_invalid
        update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return TIME
    time = time_.get_msk(time)
    currency_index = context.user_data['currency_index']
    jobs.disable_job(queue, chat_id, currency_index)
    queue.run_daily(callback=callback_rate,
                    time=time, 
                    days=Days.EVERY_DAY, 
                    context=chat_id, 
                    name=jobs.get_job_name(currency_index))
    time = time.strftime(jobs.TIME_FORMAT)
    days = ''.join( [str(x) for x in tuple(Days.EVERY_DAY)] ) 
    job = Job( currency_index, time, days=days, id=Id(chat_id, user_id) )  
    
    jobs.add_job(job)
    text = BotResponse.job_stated(currency_index, time)
    update.message.reply_text(text=text, 
                              parse_mode=ParseMode.HTML,
                              reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def callback_rate(context):
    '''Function is called by job. User get actual rate of currecy.'''
    chat_id = context.job.context
    currency_index = jobs.get_currency_index(context.job.name)
    currencies = Currencies()
    currency_name = currencies.get_name(currency_index)
    webset = currencies.get_webset(currency_index)
    currency_rate = BotWebModel().get_element_text(webset.url, webset.selector)
    text = BotResponse.rate( list([currency_index, currency_name, webset.unit, currency_rate]) )
    context.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)

@run_async
def rate(update, context):
    '''User get actual rate of request currecy.'''
    user_currency = Regex().match(Patterns.CURRENCY, update.message.text)
    currencies = Currencies()
    currency_index = currencies.get_index(user_currency)
    if not currency_index:
        text = BotResponse.conv_currency_invalid(user_currency)
        update.message.reply_text(text,
                                  parse_mode=ParseMode.HTML)
        context.chat_data['conv'] = RATE
        return RATE
    update.message.reply_text(text=BotResponse.request_accept, 
                              reply_markup=ReplyKeyboardRemove())
    webset = currencies.get_webset(currency_index)
    currency_name = currencies.get_name(currency_index)
    currency_rate = BotWebModel().get_element_text(webset.url, webset.selector)

    text = BotResponse.rate(list([currency_index, currency_name, webset.unit, currency_rate]))
    update.message.reply_text(text, parse_mode=ParseMode.HTML)
    context.user_data.clear()
    return ConversationHandler.END

@run_async
def cancel(update, context):
    '''End any conversation is use.'''
    text = BotResponse.conv_cancel
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END


def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    jobs.init(dp.job_queue, callback_rate)
    
    dp.add_handler(CommandHandler('notifications', notifications))
    dp.add_handler(MessageHandler(ReFilter(Patterns.NOTIFY_FORCE), notify_force))
    dp.add_handler(MessageHandler(ReFilter(Patterns.NOTIFY_DISABLE), disable))

    currency_conversation_handler = ConversationHandler(
        entry_points= [ MessageHandler(ReFilter(Patterns.RATE_MASK), rate),
                        MessageHandler(ReFilter(Patterns.CURRENCY_MASK), notify),
                        CommandHandler('rate', conv_currency),
                        CommandHandler('notify', conv_currency) ],
        states = {
            RATE: [ MessageHandler(ReFilter(Patterns.CURRENCY_SHOW_MORE), conv_currency),
                    MessageHandler(~ReFilter(Patterns.FALLBACK), rate) ],
            NOTIFY: [ MessageHandler(ReFilter(Patterns.CURRENCY_SHOW_MORE), conv_currency),
                        MessageHandler(~ReFilter(Patterns.FALLBACK), notify) ],
            TIME: [ MessageHandler(ReFilter(Patterns.TIME_CONV), time) ],
        },
        fallbacks = [MessageHandler(ReFilter(Patterns.FALLBACK), cancel)]
    )
    
    dp.add_handler(currency_conversation_handler)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', start))
    dp.add_handler(MessageHandler(Filters.all, start))
    updater.bot.set_my_commands(BotModel.BOT_COMMANDS)
    updater.start_polling(2.0)
    updater.idle()

if __name__ == '__main__':
    main()