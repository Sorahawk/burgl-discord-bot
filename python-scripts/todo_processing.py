import global_constants

from global_constants import *
from storage_functions import *

from re import findall, IGNORECASE


# returns processed task description and its priority level as a tuple of strings
def process_todo_input(user_input):
	# split user input into individual words
	split_input = user_input.lower().strip().split()

	# default priority level is medium
	priority_level = 'Medium'

	if split_input:
		# check front and back for presence of priority level
		front, back = split_input[0], split_input[-1]

		# check from highest to lowest priority
		for level in TODO_PRIORITY_LEVELS[::-1]:
			lowered_level = level.lower()

			# either match the first letter or the entire priority word, no in-betweens
			if front in [lowered_level[0], lowered_level]:
				priority_level = level

				# partition() returns a tuple (preceding string, string match, following string)
				user_input = user_input.partition(front)[2]
				break

			if back in [lowered_level[0], lowered_level]:
				priority_level = level

				# rpartition() also returns same type of tuple as partition()
				user_input = user_input.rpartition(back)[0]
				break

	return user_input.strip(), priority_level


# extracts all valid task IDs from user input and
# returns the list of task IDs as well processed user input
def extract_task_id(user_input):
	number_length = len(str(MAXIMUM_ID))
	regex_pattern = f'[a-z][0-9]{{{number_length}}}'

	split_input = user_input.split()
	id_list = []

	for word in split_input:
		is_task_id = findall(regex_pattern, word, IGNORECASE)

		if is_task_id:
			task_id = is_task_id[0]

			# raise the task ID letter to uppercase since it is stored as such in DynamoDB
			id_list.append(task_id.upper())
			user_input = user_input.replace(task_id, '')

	# split and rejoin user input to remove excess whitespace
	user_input = ' '.join(user_input.split())

	return user_input, id_list
