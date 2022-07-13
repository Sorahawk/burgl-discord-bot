import global_constants

from re import findall, IGNORECASE

from global_constants import *
from storage_functions import *


# returns processed task description and its priority level as a tuple of strings
def process_todo_input(user_input):
	# split user input into individual words
	regex_pattern = '[a-z]+[\W_]'

	# insert surrounding whitespace so leading and trailing task IDs can be detected
	user_input = f' {user_input} '

	results = findall(regex_pattern, user_input, IGNORECASE)

	# default priority level is medium
	priority_level = 'Medium'

	# just use default level if no valid input was detected
	if results:
		# check front and back for presence of priority level
		front, back = results[0][:-1], results[-1][:-1]

		for level in TODO_PRIORITY_LEVELS:
			if front in level.lower():
				priority_level = level
				user_input = user_input.partition(front)[2]

			if back in level.lower():
				priority_level = level
				user_input = user_input.rpartition(back)[0]

	# lower all letters and remove edge symbols
	user_input = user_input.lower().strip('., ').replace(' ,', ',')

	return user_input, priority_level


# returns all valid task IDs provided in user input
def extract_task_id(user_input):
	number_length = len(str(MAXIMUM_ID))
	regex_pattern = f'[\W_][a-z][0-9]{{{number_length}}}[\W_]'

	# double every whitespace so it won't overlap when performing regex 
	user_input = user_input.replace(' ', '  ')

	# insert surrounding whitespace so leading and trailing task IDs can be detected
	user_input = f' {user_input} '

	regex_results = findall(regex_pattern, user_input, IGNORECASE)

	if regex_results:
		# slice each result as there are leading and trailing whitespaces/symbols
		for index in range(len(regex_results)):
			regex_results[index] = regex_results[index][1:-1].upper()

	return regex_results


# returns priority level for harvesting task based on quantity
def get_harvest_priority(quantity):
	if quantity > 150:
		return 'High'

	elif quantity > 50:
		return 'Medium'

	else:
		return 'Low'


# increases harvest amount for a given material if a harvest task for it already exists
# otherwise creates a new harvesting task for that material with the given quantity
def create_harvesting_task(material_name, quantity):
	# if already exists, retrieve the old amount and delete the existing entry first
	if material_name in global_constants.HARVEST_TASK_REFERENCE:
		# look up the existing task ID
		old_id = global_constants.HARVEST_TASK_REFERENCE[material_name]

		# get the old task description while removing the existing entry
		old_description = remove_task_scheduler(old_id)

		# calculate the new total quantity
		old_quantity = int(old_description.split()[2])
		quantity += old_quantity

	# get the task priority level based on the harvest quantity
	priority_level = get_harvest_priority(quantity)

	# fill in harvesting task description
	task_description = HARVEST_DESCRIPTION_TEMPLATE.replace('VAR1', str(quantity)).replace('VAR2', material_name)

	# insert entry into Task Scheduler
	task_id = insert_task_scheduler(priority_level, task_description)

	# update reference table
	global_constants.HARVEST_TASK_REFERENCE[material_name] = task_id


# removes all generated harvesting tasks tagged with [Chop] at the front of the task description
def remove_all_harvesting_tasks():
	for material_name, task_id in global_constants.HARVEST_TASK_REFERENCE.items():
		remove_task_scheduler(task_id)

	global_constants.HARVEST_TASK_REFERENCE = {}


def update_harvest_amount():
	pass


def edit_todo_priority():
	pass
