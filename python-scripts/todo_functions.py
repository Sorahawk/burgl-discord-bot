from discord import Embed

from bot_messaging import *
from global_constants import *


# adds a to-do entry to the Task Scheduler
async def todo_default(message, user_input):
	await message.channel.send('Task - Default')


# view current to-do tasks
async def todo_view(message, user_input):
	await message.channel.send('Task - View')


# check tasks off the Task Scheduler
async def todo_delete(message, user_input):
	await message.channel.send('Task - Delete')
