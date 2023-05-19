from aiogram import Dispatcher
from aiogram.filters import Command

from .send_schedule_message import chat_id_handler, start
from .init import get_bot
from .states import EnterData

global bot, router, dispatcher

def register_handlers(dp: Dispatcher):
    dp.message.register(start, Command(commands=["start"]))
    dp.message.register(chat_id_handler, EnterData.get_id)

async def start_bot(TOKEN):
    global bot, router, dispatcher

    bot, router, dispatcher = get_bot(TOKEN)

    register_handlers(dispatcher)

    await dispatcher.start_polling(bot, skip_updates=True)
