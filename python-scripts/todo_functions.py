import var_global

from var_global import *
from bot_messaging import *
from todo_processing import *
from dynamodb_methods import *
from storage_functions import *
from string_processing import *

from math import ceil
from discord import Embed


# adds a to-do entry to the Task Scheduler
async def todo_default(message, user_input):
	# process input to separate priority level from description
	task_description, task_priority = process_todo_input(user_input)

	if not task_description:
		return await burgl_message('empty', message)

	# insert new entry into Task Scheduler
	task_id = insert_task_scheduler(task_priority, task_description)

	embed_title = '**New To-Do Entry**'
	summary_embed = Embed(title=embed_title, color=EMBED_COLOR_CODE)

	summary_embed.add_field(name=f'Task {task_id}', value=task_description_capitalisation(task_description), inline=False)

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

			todo_embed.add_field(name=f'{task_id}', value=task_description_capitalisation(task_description), inline=False)

		todo_embed.set_footer(text=f'Page {page + 1}/{number_pages}')
		embed_list.append(todo_embed)

	return await multipage_embed_handler(message, user_input, embed_list)


# find tasks with descriptions matching the given input
async def todo_find(message, user_input):
	user_input = user_input.lower()

	todo_list = retrieve_task_scheduler_sorted()
	matching_tasks = []

	# iterate through task list in descending priority and check each description
	for priority_level in TODO_PRIORITY_LEVELS[::-1]:
		for todo_task in todo_list[priority_level[0]]:
			task_id = todo_task[0]
			task_description = todo_task[1]

			if user_input in task_description.lower():
				matching_tasks.append((task_id, task_description))

	# process matches into pages and display
	embed_list = []
	number_pages = ceil(len(matching_tasks) / MAX_TODO_FIELDS)

	for page in range(number_pages):
		find_embed = Embed(title=f"**Task Search: '{task_description_capitalisation(user_input)}'**", color=EMBED_COLOR_CODE)

		start_index = page * MAX_TODO_FIELDS
		end_index = start_index + MAX_TODO_FIELDS

		for entry in matching_tasks[start_index:end_index]:
			task_id = entry[0]
			task_description = entry[1]

			find_embed.add_field(name=f'{task_id}', value=task_description_capitalisation(task_description), inline=False)

		find_embed.set_footer(text=f'Page {page + 1}/{number_pages}')
		embed_list.append(find_embed)

	return await multipage_embed_handler(message, user_input, embed_list)


# edit priority of one or more tasks
async def todo_edit(message, user_input):
	# get list of entered task IDs
	user_input, id_list = extract_task_id(user_input)

	if not id_list:
		return await burgl_message('empty', message)

	# extract priority level from user input
	new_description, task_priority = process_todo_input(user_input)

	embed_title = '**Edited To-Do Entries**'
	summary_embed = Embed(title=embed_title, color=EMBED_COLOR_CODE)

	for task_id in id_list:
		task_description = remove_task_scheduler(task_id)

		# if given task ID did not exist, display error for that task ID
		if not task_description:
			await detect_errors(message, f'Task {task_id}', 106)
			continue

		# remove task ID from new description
		new_description = new_description.replace(id_list[0].upper(), '').replace(id_list[0].lower(), '').strip()

		if len(id_list) == 1 and new_description:
			task_description = new_description

		# insert new entry with the new priority level
		new_id = insert_task_scheduler(task_priority, task_description)

		task_description = task_description_capitalisation(task_description)
		summary_embed.add_field(name=f'{task_id} -> {new_id}', value=task_description, inline=False)

	# only send embed if valid items were added
	if len(summary_embed) != len(embed_title):
		await message.channel.send(embed=summary_embed)


# check one or more tasks off the Task Scheduler
async def todo_delete(message, user_input):
	user_input, id_list = extract_task_id(user_input)

	# check if any valid input was provided
	if not id_list:
		return await burgl_message('empty', message)

	embed_title = '**Completed Tasks**'
	summary_embed = Embed(title=embed_title, color=EMBED_COLOR_CODE)

	# slice each result as there are leading and trailing whitespaces/symbols
	for task_id in id_list:
		# try to delete each task ID
		task_description = remove_task_scheduler(task_id)

		# if given task ID did not exist, display error for that task ID
		if not task_description:
			await detect_errors(message, f'Task {task_id}', 106)
			continue

		summary_embed.add_field(name=f'{task_id}', value=task_description_capitalisation(task_description), inline=False)

	# only send embed if valid items were added
	if len(summary_embed) != len(embed_title):
		await message.channel.send(embed=summary_embed)


# wipe the entire Task Scheduler
async def todo_reset(message, user_input):
	if 'confirm' not in user_input.lower():
		return await burgl_message('need_confirmation', message)

	# wipe the entire DynamoDB table
	ddb_remove_all(TASK_TABLE)

	await burgl_message('list_reset', message)
