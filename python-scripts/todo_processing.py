from re import findall, IGNORECASE

from global_constants import *


# returns processed task details and its priority level as a tuple of strings
def process_todo_input(user_input):
	# split user input into individual words
	regex_pattern = '[a-z]+'
	results = findall(regex_pattern, user_input, IGNORECASE)

	# check front and back for presence of priority level
	front, back = results[0], results[-1]

	# default priority level is medium
	priority_level = 'Medium'

	for level in TODO_PRIORITY_LEVELS:
		if front in level.lower():
			priority_level = level
			user_input = user_input.partition(front)[2]

		if back in level.lower():
			priority_level = level
			user_input = user_input.rpartition(back)[0]

	# remove edge symbols
	user_input = user_input.strip('., ').replace(' ,', ',')

	return user_input, priority_level


def insert_todo_item():
	pass



def create_harvesting_task():
	# create new task for that material if doesn't exist
	# otherwise update the amount to reflect increase
	pass


def update_harvest_amount():
	pass


def edit_todo_priority():
	pass


def remove_todo_item():
	pass

