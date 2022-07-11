from re import findall, IGNORECASE

from global_constants import *


# returns processed task description and its priority level as a tuple of strings
def process_todo_input(user_input):
	# split user input into individual words
	regex_pattern = ' [a-z]+ '

	# insert surrounding whitespace so leading and trailing task IDs can be detected
	user_input = f' {user_input} '

	results = findall(regex_pattern, user_input, IGNORECASE)

	# default priority level is medium
	priority_level = 'Medium'

	# just use default level if no valid input was detected
	if results:
		# check front and back for presence of priority level
		front, back = results[0].strip(), results[-1].strip()

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


def create_harvesting_task():
	# create new task for that material if doesn't exist
	# otherwise update the amount to reflect increase
	pass


def update_harvest_amount():
	pass


def edit_todo_priority():
	pass
