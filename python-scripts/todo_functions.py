from discord import Embed

from bot_messaging import *
from todo_processing import *
from global_constants import *
from storage_functions import *
from string_processing import *


# adds a to-do entry to the Task Scheduler
async def todo_default(message, user_input):
	# process input to separate priority level from details
	todo_task, priority_level = process_todo_input(user_input)

	# insert new entry into Task Scheduler
	task_id = update_task_scheduler(todo_task, priority_level)

	embed_title = '**New To-Do Task**'
	summary_embed = Embed(title=embed_title, color=EMBED_COLOR_CODE)

	summary_embed.add_field(name=f'Task {task_id}', value=capitalise_object_name(todo_task))

	await message.channel.send(embed=summary_embed)


# view current to-do tasks
async def todo_view(message, user_input):
	await message.channel.send('Task - View')

	# TODO: apply custom capitalisation algorithm when displaying the task
	# user_input = capitalise_object_name(user_input)


# check tasks off the Task Scheduler
async def todo_delete(message, user_input):
	await message.channel.send('Task - Delete')
