import logging
import os
import sys

from aiogram import Bot
from aiogram import Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy

def get_bot(TOKEN):
    bot = Bot(token=TOKEN)

    ro = Router()
    dp = Dispatcher(bot=bot, storage=MemoryStorage(), fsm_strategy=FSMStrategy.USER_IN_CHAT)
    dp.include_router(ro)


    current_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)

    logging.basicConfig(level=logging.INFO)

    return bot, ro, dp
