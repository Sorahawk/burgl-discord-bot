from dynamodb_methods import *
from global_variables import *


# binds one or more shortcut phrases to a full name
def bind_query_name(full_name, shortcuts):
	table_name = SHORTCUT_STORAGE
	added_items = []

	for shortcut in shortcuts:
		shortcut = shortcut.strip()  # remove preceding whitespace before each word, e.g. 'a, b, c'
		ddb_insert_item(table_name, shortcut, full_name)


# returns full name corresponding to a given shortcut if it exists, otherwise returns None by default
def get_full_name(shortcut):
	table_name = SHORTCUT_STORAGE
	attribute_header = get_table_headers(table_name)[1]

	full_name = ddb_retrieve_item(table_name, search_query)

	if full_name:
		return full_name[attribute_header]
