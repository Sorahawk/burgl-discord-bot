from random import randint
from collections import Counter

from secrets import *
from dynamodb_methods import *
from global_constants import *
from string_processing import *


# binds one or more shortcut phrases to a full name
def bind_shortcuts(full_name, shortcuts):
	added_items = []
	display_name = capitalise_object_name(full_name)

	formatted_string = f'Case-insensitive shortcuts added for **{display_name}**:\n'

	for short_name in shortcuts:
		short_name = short_name.strip()  # remove preceding whitespace before each word, e.g. 'a, b, c'
		result = ddb_insert_item(SHORTCUT_TABLE, short_name, full_name)

		if result:
			formatted_string += f'- {short_name}\n'

			# remove entry from object info cache with short_name as the key, if any
			ddb_remove_item(INFO_TABLE, short_name)

	return formatted_string


# returns corresponding full name if input is an existing shortcut, otherwise just returns the original input
def retrieve_full_name(search_query):
	table_name = SHORTCUT_TABLE
	attribute_header = get_table_headers(table_name)[1]

	full_name = ddb_retrieve_item(table_name, search_query.lower())

	# if entry exists in table
	if full_name:
		search_query = full_name[attribute_header]

	return search_query


# returns a list of tuples, sorted alphabetically by object name which is first item in the tuple
# second item in each tuple is a list of the corresponding shortcuts
def retrieve_all_shortcuts():
	table_name = SHORTCUT_TABLE
	shortcuts = {}

	short_header, full_header = get_table_headers(table_name)

	# it is almost impossible for this shortcut table to cross the 1MB limit as it would take at least 24k entries
	# so one table.scan() will be enough to retrieve the entire table
	items = ddb_retrieve_all(table_name)

	for binded_pair in items:
		short_name = binded_pair[short_header]
		full_name = capitalise_object_name(binded_pair[full_header])

		if full_name not in shortcuts:
			shortcuts[full_name] = [short_name]
		else:
			shortcuts[full_name].append(short_name)
			shortcuts[full_name].sort()

	return sorted(shortcuts.items())


# delete all shortcuts from one or more given full names
def delete_shortcut(full_name, all_shortcuts):
	full_name = capitalise_object_name(full_name)

	# check if given full name exists in storage
	# for each binded shortcut, remove it from storage 
	if full_name not in all_shortcuts:
		return 106

	for short_name in all_shortcuts[full_name]:
		ddb_remove_item(SHORTCUT_TABLE, short_name)


# returns corresponding attribute value if it exists in table, otherwise None by default
def retrieve_from_cache(table_name, key):
	if not DEBUG_MODE:
		attribute_header = get_table_headers(table_name)[1]
		result = ddb_retrieve_item(table_name, key)

		if result:
			return result[attribute_header]


# clear the cache tables (query-object info and url-HTML)
def clear_cache():
	tables = [INFO_TABLE, HTML_TABLE]

	for table_name in tables:
		ddb_remove_all(table_name)


# checks for existing quantity for a specific item in Chopping List and updates it appropriately
def update_chopping_list(item_name, quantity, base_components, ignore_existing=False):
	table_name = CHOPPING_TABLE
	quantity_header, components_header = get_table_headers(table_name)[1]

	if ignore_existing:
		existing_entry = None
	else:
		existing_entry = ddb_retrieve_item(table_name, item_name)

	if existing_entry:
		quantity += existing_entry[quantity_header]
		base_components += Counter(existing_entry[components_header])

	ddb_insert_item(table_name, item_name, (quantity, base_components))


# returns a list of tuples, sorted alphabetically by item name, which is the first item in each tuple
# second item of each tuple is item quantity, and third item is corresponding components
def retrieve_chopping_list():
	table_name = CHOPPING_TABLE
	chopping_list = {}

	item_header, (quantity_header, components_header) = get_table_headers(table_name)
	list_entries = ddb_retrieve_all(table_name)

	for entry in list_entries:
		item_name = entry[item_header]
		quantity = entry[quantity_header]
		components = entry[components_header]

		chopping_list[item_name] = quantity, components

	return sorted(chopping_list.items())


# returns a random but unique Task Scheduler ID
def generate_task_id(priority_level=None):
	if not priority_level:
		priority_level = 'Medium'

	task_id = None

	while not task_id:
		numeric_id = str(randint(1, MAXIMUM_ID))

		# pad numeric ID with leading zero if not full-length
		while len(numeric_id) < len(str(MAXIMUM_ID)):
			numeric_id = f'0{numeric_id}'

		task_id = priority_level[0] + numeric_id

		if not ddb_retrieve_item(TASK_TABLE, task_id):
			return task_id

		task_id = None


# either inserts a new entry into the Task Scheduler or edits an existing task
# returns the task ID of the inserted task
def update_task_scheduler(task_priority, task_description=None, task_id=None):
	table_name = TASK_TABLE
	description_header = get_table_headers(table_name)[1]

	# if task ID is provided, delete the existing entry before creating a new one
	if task_id:
		existing_entry = ddb_retrieve_item(table_name, task_id)

		# confirm that given task ID exists
		if not existing_entry:
			return False

		if not task_description:
			task_description = existing_entry[description_header]

		# delete existing entry
		ddb_remove_item(table_name, task_id)

	# generate task ID
	task_id = generate_task_id(task_priority)

	# insert task entry
	ddb_insert_item(table_name, task_id, task_description)

	return task_id, task_description


# returns a dictionary where the item key is the task ID and corresponding value is the task description
def retrieve_task_scheduler_flat():
	table_name = TASK_TABLE
	todo_list = {}

	id_header, description_header = get_table_headers(table_name)
	list_entries = ddb_retrieve_all(table_name)

	for entry in list_entries:
		task_id = entry[id_header]
		task_description = entry[description_header]

		todo_list[task_id] = task_description

	return todo_list


# returns a dictionary of lists, where each key is the first character of the priority level
# each list contains tasks of that corresponding priority level
# each item in the list is a tuple, first item is the task ID and the second is the task description
def retrieve_task_scheduler_sorted():
	table_name = TASK_TABLE
	todo_list = {}

	for priority_level in TODO_PRIORITY_LEVELS:
		todo_list[priority_level[0]] = []

	id_header, description_header = get_table_headers(table_name)
	list_entries = ddb_retrieve_all(table_name)

	for entry in list_entries:
		task_id = entry[id_header]
		task_description = entry[description_header]

		task = (task_id, task_description)
		todo_list[task_id[0]].append(task)

	for key in todo_list:
		todo_list[key].sort()

	return todo_list
