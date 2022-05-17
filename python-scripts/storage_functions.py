from dynamodb_methods import *
from global_variables import *

from secret_variables import DEBUG_MODE
from string_processing import capitalise_object_name


# binds one or more shortcut phrases to a full name
def bind_shortcuts(full_name, shortcuts):
	added_items = []
	display_name = capitalise_object_name(full_name)

	formatted_string = f'Case-insensitive shortcuts added for **{display_name}**:\n'

	for short_name in shortcuts:
		short_name = short_name.strip()  # remove preceding whitespace before each word, e.g. 'a, b, c'
		result = ddb_insert_item(SHORTCUT_STORAGE, short_name, full_name)

		if result:
			formatted_string += f'- {short_name}\n'

			# remove entry from object info cache with short_name as the key, if any
			ddb_remove_item(OBJECT_INFO_CACHE, short_name)

	return formatted_string


# returns corresponding full name if it exists in table, otherwise just returns the original input
def retrieve_full_name(search_query):
	table_name = SHORTCUT_STORAGE
	attribute_header = get_table_headers(table_name)[1]

	full_name = ddb_retrieve_item(table_name, search_query.lower())

	# if entry exists in table
	if full_name:
		search_query = full_name[attribute_header]

	return search_query


# returns a list of tuples, sorted alphabetically by object name which is first item in the tuple
# second item in each tuple is a list of the corresponding shortcuts
def retrieve_all_shortcuts():
	shortcuts = {}

	# it is almost impossible for this shortcut table to cross the 1MB limit as it would take at least 24k entries
	# so one table.scan() will be enough to retrieve the entire table
	items = ddb_retrieve_all(SHORTCUT_STORAGE)

	for binded_pair in items:
		full_name = capitalise_object_name(binded_pair['full_name'])
		short_name = binded_pair['short_name']

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
				result = ddb_remove_item(SHORTCUT_STORAGE, short_name)

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


# purge the cache tables (query-object info and url-HTML)
def purge_cache():
	tables = [OBJECT_INFO_CACHE, PAGE_HTML_CACHE]

	for table_name in tables:
		ddb_remove_all(table_name)
