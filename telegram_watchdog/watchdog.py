#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import pendulum
from datetime import datetime
from pydantic import BaseModel
import ping3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    filters, 
    MessageHandler, 
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes, 
    CallbackQueryHandler
)
from config.config import Settings

settings = Settings()

class host2CheckClass(BaseModel):
    name: str
    address: str
    status: bool = None
    response_time: datetime = datetime.now()

    def __repr__(self):
        match self.status:
            case True:
                emoji = '\u2705'
            case False:
                emoji = '\u274C'
            case _:
                emoji = '\u2754'

        formatted_time = self.response_time.strftime("%d-%m-%y %H:%M")
        return f'{emoji} [{self.name}] - {self.address} - _{formatted_time}_'


    def set_status(self, status):
        self.status = status

    def set_response_time(self):
        self.response_time = datetime.now()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Itera por los hosts
host_objects = [
    host2CheckClass(
        name=host_dict.get('name'), address=host_dict.get('address')
        ) for host_dict in settings.HOST2CHECK]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            (
                InlineKeyboardButton(host_objects[i].name, callback_data=str(i+1))
            ) for i in range(len(host_objects))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please container to restart:", reply_markup=reply_markup)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=update.message.text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Use /set /stop to execute MASTRO_bot.")


async def check_internet(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    logging.info(job.data)
    response_time = ping3.ping(job.data.address)
    msg = f'{pendulum.now(settings.TZ).format("DD-MM-YY HH:mm")} [{job.data.name}]'
    if response_time is not False and response_time is not None:
        if job.data.status is False or job.data.status is None:
            job.data.set_response_time()
            await context.bot.send_message(job.chat_id,
                                           text=f"\u2705 {msg} is alive")
        job.data.set_status(True)
    else:
        if job.data.status is True or job.data.status is None:
            job.data.set_response_time()
            await context.bot.send_message(job.chat_id,
                                           text=f"\u274C {msg} is down")
        job.data.set_status(False)


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    try:
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)

        # Itera por los objetos hosts
        for host_class in host_objects:
            context.job_queue.run_repeating(
                check_internet, 
                interval=due, 
                chat_id=chat_id, 
                name=str(chat_id), 
                data=host_class)

        text = "Timer successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds>")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for host_class in host_objects:
        await update.message.reply_text(f'{host_class.__repr__()}', parse_mode= 'Markdown')


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Demo Selected: {query.data}")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.")


def main():
    application = ApplicationBuilder().token(settings.TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
