import re

from global_variables import *
from collections import Counter
from difflib import SequenceMatcher


# removes bot command from front of string input
def remove_command_prefix(input_string, command):
	return input_string[len(command):].strip()


# check for a specified command flag, and returns True/False, along with modified search query
def check_command_flag(search_query, flag_key):
	command_flag = BOT_COMMAND_FLAGS[flag_key]
	search_query = search_query + ' '

	result = False
	if command_flag in search_query.lower():
		result = True

	# if flag not in query, replacing won't affect the string
	search_query = search_query.replace(command_flag, '').replace(command_flag.upper(), '')
	return result, search_query.strip()


# returns page URL, comprised of sanitised search query appended to the base wiki URL
def get_appended_url(search_query):
	if '.' in search_query:
		# raise all letters for robot and device names, e.g. BURG.L, TAYZ.T, MIX.R
		return f'{BASE_WIKI_URL}{search_query.upper()}'

	# symbols to ignore from user input as most of these will cause a 'Bad Title' page on the wiki
	illegal_symbols = '[\][}{><|%+]+'

	search_query = re.sub(illegal_symbols, '', search_query)

	# replace ? with %3F, e.g. Smoothie?
	search_query = search_query.replace('?', '%3F')

	# check if 'arrows' is the last word and remove the trailing S
	if search_query.strip()[-6:].lower() == 'arrows':
		search_query = search_query[:-1]

	# capitalise the first letter of every word as the webpage URL is case sensitive
	# at one point, used string.capwords() because title() capitalises the letter after an apostrophe, but capwords does not raise anything behind a bracket either
	search_query = search_query.title().replace("'S", "'s")
	return f'{BASE_WIKI_URL}{search_query}'


# returns ratio of similarity between two input strings
def string_similarity(a, b):
	return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# processes the many variations of (e)weakness and (e)resistance labels with a single function
# returns the specific header (out of 4 possibilities) and the processed string
def weakness_resistance_processing(header, content):
	if 'weakness' in header:
		keyword = 'weakness'
	else:
		keyword = 'resistance'

	header = header.split(keyword)
	if header[0] == 'e':
		keyword = f'e{keyword}'

	return keyword, content.replace('-or-', ', ')


# returns a Counter() of the compiled materials and their quantities
# collections.Counter will make it much easier to recursively sum up materials for chopping list in future
def compile_counter(item_list, recipe_type=None):
	counter = Counter()
	value = None

	for item in item_list:
		if item.strip():
			if recipe_type == 'Smoothie':
				counter[item] = 1
			elif value is None:
				value = item
			else:
				counter[value] = int(item)
				value = None

	return counter


# detect special smoothie type from user input and remove it
# returns new search query and the smoothie type as two separate variables
# returns 'basic' by default since don't expect basic to be explicitly stated for smoothies
def detect_smoothie_type(search_query):
	smoothie_type = 'basic'

	# detect any special smoothie types from input, e.g. beefy, sticky
	# does not account for multiple smoothie types, will just take the last one iterated
	for special in SMOOTHIE_BASES:
		# ignore 'basic' base because it might appear in other items, e.g. Normal Chair
		if special != 'basic' and special in search_query.lower():
			new_search_query = re.compile(special, re.IGNORECASE).sub('', search_query).strip()

			# if the input was just the smoothie type alone, do not remove it
			if new_search_query:
				search_query = new_search_query
				smoothie_type = special

	return search_query, smoothie_type


# returns booleans representing presence of recipe and repair costs on an object's page
def check_info_presence(page_content):
	has_recipe = True
	has_repair_cost = False

	try:
		page_content.get_element_by_id('Recipe')
	except KeyError:
		has_recipe = False

	if 'Repair Cost' in page_content.itertext():
		has_repair_cost = True

	return has_recipe, has_repair_cost


# removes one newline from the end of the string if there are two
# returns processed string
def remove_extra_newline(formatted_string):
	if formatted_string[-2:] == '\n\n':
		formatted_string = formatted_string[:-1]
	return formatted_string



# suffix pet icon emoji to the name of corresponding tameable creature
def pet_icon_emoji(formatted_string, creature_name):
	return formatted_string.replace(creature_name, f'{creature_name} {CUSTOM_EMOJIS[creature_name]}')


# suffix custom emoji to damage and elemental types
def damage_elemental_emoji(input_string):
	for keyword in CUSTOM_EMOJIS:
		input_string = input_string.replace(keyword, f'{CUSTOM_EMOJIS[keyword]}{keyword}')

	return input_string
