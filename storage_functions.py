from dynamodb_methods import *
from global_variables import *
from helper_functions import check_command_flag


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
# if command flag to bypass shortcuts is present, then just return the original query
def retrieve_full_name(search_query):

	# check for command flag that signals to ignore any shortcut bindings
	search_actual, search_query = check_command_flag(search_query, 'force_search')

	if not search_actual:
		table_name = SHORTCUT_STORAGE
		attribute_header = get_table_headers(table_name)[1]

		full_name = ddb_retrieve_item(table_name, search_query.lower())

		if full_name:
			return full_name[attribute_header]

	return search_query


# returns corresponding page HTML if it exists, otherwise None by default
def retrieve_page_html(wiki_url):
	table_name = PAGE_HTML_CACHE
	attribute_header = get_table_headers(table_name)[1]

	html_string = ddb_retrieve_item(table_name, wiki_url)

	if html_string:
		return html_string[attribute_header]
