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
def delete_shortcuts(full_names):
	string_header = 'All shortcuts removed for the following:\n'
	formatted_string = ''

	shortcuts = dict(retrieve_all_shortcuts())

	for full_name in full_names:
		full_name = capitalise_object_name(full_name)

		# check if given full name exists in storage
		if full_name in shortcuts:

			# for each binded shortcut, remove it from storage 
			for short_name in shortcuts[full_name]:
				result = ddb_remove_item(SHORTCUT_TABLE, short_name)

				if not result:
					# if deletion of any shortcut fails, break out of the loop
					break

			if result:
				formatted_string += f'- **{capitalise_object_name(full_name)}**\n'

	return string_header + formatted_string if formatted_string else None


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
# returns ddb_insert_item(), which itself returns True for successful insertions, otherwise False
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

	return ddb_insert_item(table_name, item_name, (quantity, base_components))


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
def generate_random_id(priority_level):
	task_id = None

	while not task_id:
		numeric_id = str(randint(1, 99))

		# pad numeric ID with leading zero if not double-digit
		if len(numeric_id) == 1:
			numeric_id = f'0{numeric_id}'

		task_id = priority_level[0].upper() + numeric_id

		if not ddb_retrieve_item(TASK_TABLE, task_id):
			return task_id

		task_id = None


# either inserts a new entry into the Task Scheduler
# or updates an existing task's description and/or priority
def update_task_scheduler(task_description, task_priority, task_id=None):
	table_name = TASK_TABLE

	# TODO: update task info
	if task_id:

		# TODO: if task_priority doesn't match first letter of task_id
		# delete old task_id entry and create new one

		return

	# generate task ID
	task_id = generate_random_id(task_priority)

	# insert task entry
	ddb_insert_item(table_name, task_id, task_description)

	return task_id
