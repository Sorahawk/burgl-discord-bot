import re, string

from collections import Counter
from difflib import SequenceMatcher


# sanitises search query and appends it to base wiki URL, and returns result 
def get_appended_url(search_query):
	illegal_symbols = '[\][}{><|%+]+'

	# sanitise input as these symbols will cause a 'Bad Title' page on the wiki
	search_query = re.sub(illegal_symbols, '', search_query)

	# replace ? with %3F
	search_query = search_query.replace('?', '%3F')

	# check if 'arrows' is the last word and remove the trailing S
	if search_query.strip()[-6:].lower() == 'arrows':
		search_query = search_query[:-1]

	# capitalise the first letter of every word as the webpage URL is case sensitive
	# initially used .title() but then realised that it also capitalises the letter after an apostrophe
	return f'https://grounded.fandom.com/wiki/{string.capwords(search_query)}'


# returns ratio of similarity between two input strings
def string_similarity(a, b):
	return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def weakness_resistance_processing(header, content):
	if 'weakness' in header:
		keyword = 'weakness'
	else:
		keyword = 'resistance'

	header = header.split(keyword)
	if header[0] == 'e':
		keyword = f'e{keyword}'

	return keyword, content.replace('-or-', ', ')


# compiles materials into a Counter() and returns it
# collections.Counter will make it much easier to recursively sum up materials for chopping list
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


# removes one newline from the end of the string if there are two
def remove_extra_newline(formatted_string):
	if formatted_string[-2:] == '\n\n':
		formatted_string = formatted_string[:-1]
	return formatted_string


# prefix a 0 if stat is just '.5'
def prefix_zero(content):
	if content == '.5':
		content = f'0{content}'
	return content
