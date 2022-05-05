from dynamodb_methods import *
from global_variables import *


# binds one or more shortcut phrases to a full name
def bind_query_name(full_name, shortcuts):
	table_name = SHORTCUT_STORAGE
	added_items = []

	formatted_string = f"Case-insensitive shortcuts added for **'{full_name}'**:\n"

	for shortcut in shortcuts:
		shortcut = shortcut.strip()  # remove preceding whitespace before each word, e.g. 'a, b, c'
		result = ddb_insert_item(table_name, shortcut, full_name)

		if result:
			formatted_string += f"-{shortcut}\n"

	return formatted_string


# returns corresponding full name if it exists, otherwise just returns the original input
def get_full_name(search_query):
	table_name = SHORTCUT_STORAGE
	attribute_header = get_table_headers(table_name)[1]

	full_name = ddb_retrieve_item(table_name, search_query.lower())

	if full_name:
		return full_name[attribute_header]
	else:
		return search_query
