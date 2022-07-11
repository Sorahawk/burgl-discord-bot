from math import ceil
from discord import Embed

from bot_messaging import *
from todo_processing import *
from dynamodb_methods import *
from global_constants import *
from storage_functions import *
from string_processing import *


# adds a to-do entry to the Task Scheduler
async def todo_default(message, user_input):
	# process input to separate priority level from details
	task_description, task_priority = process_todo_input(user_input)

	# insert new entry into Task Scheduler
	task_id = update_task_scheduler(task_description, task_priority)

	embed_title = '**New To-Do Entry**'
	summary_embed = Embed(title=embed_title, color=EMBED_COLOR_CODE)

	summary_embed.add_field(name=f'Task {task_id}', value=capitalise_object_name(task_description), inline=False)

	await message.channel.send(embed=summary_embed)


# view current to-do tasks
async def todo_view(message, user_input):
	todo_list = retrieve_task_scheduler_sorted()
	sorted_todo_list = []

	# iterate through priority levels in descending order
	for priority_level in TODO_PRIORITY_LEVELS[::-1]:
		sorted_todo_list += todo_list[priority_level[0]]

	embed_list = []
	number_pages = ceil(len(sorted_todo_list) / MAX_TODO_FIELDS)

	for page in range(number_pages):
		todo_embed = Embed(title='**Task Scheduler**', color=EMBED_COLOR_CODE)

		start_index = page * MAX_TODO_FIELDS
		end_index = start_index + MAX_TODO_FIELDS

		for entry in sorted_todo_list[start_index:end_index]:
			task_id = entry[0]
			task_description = entry[1]

			todo_embed.add_field(name=f'{task_id}', value=capitalise_object_name(task_description), inline=False)

		todo_embed.set_footer(text=f'Page {page + 1}/{number_pages}')
		embed_list.append(todo_embed)

	return await multipage_embed_handler(message, user_input, embed_list)


# check one or more tasks off the Task Scheduler
async def todo_delete(message, user_input):
	regex_pattern = '[\W_][a-z][0-9]{3}[\W_]'

	# double every whitespace so it won't overlap when performing regex 
	user_input = user_input.replace(' ', '  ')

	# insert surrounding whitespace so leading and trailing task IDs can be detected
	user_input = f' {user_input} '

	regex_results = findall(regex_pattern, user_input, IGNORECASE)

	# check if any valid input was provided
	if not regex_results:
		return await burgl_message('empty', message)

	string_header = 'Tasks checked off the Task Scheduler:\n'
	formatted_string = ''

	todo_list = retrieve_task_scheduler_flat()

	# slice each result as there are leading and trailing whitespaces/symbols
	for index in range(len(regex_results)):
		task_id = regex_results[index][1:-1].upper()

		# check if given task ID exists
		if task_id not in todo_list:
			await detect_errors(message, f'Task {task_id}', 106)
			continue


		# TODO: port the below out into a processing function for deleting a given task

		# delete each task ID
		ddb_remove_item(TASK_TABLE, task_id)

		task_description = capitalise_object_name(todo_list[task_id])
		formatted_string += f'- **{task_id}**: {task_description}\n'

	if formatted_string:
		await message.channel.send(string_header + formatted_string)


# edit task priority and/or description
async def todo_edit(message, user_input):
	await message.channel.send('Task - Edit')
