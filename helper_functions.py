import re, string

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
