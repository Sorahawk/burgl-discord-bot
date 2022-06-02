from discord import Embed

from bot_messaging import *
from global_variables import *


# adds a to-do entry to the Task Scheduler
async def task_default(message, user_input):
	await message.channel.send('Task - Default')


# view current to-do tasks
async def task_view(bot, message, user_input):
	await message.channel.send('Task - View')


# check tasks off the Task Scheduler
async def task_delete(message, user_input):
	await message.channel.send('Task - Delete')
