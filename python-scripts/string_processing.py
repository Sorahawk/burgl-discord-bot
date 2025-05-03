import global_constants

from global_constants import *

from difflib import SequenceMatcher
from re import IGNORECASE, Match, sub


# determines if user input contains any command
# if no command detected, returns None
# otherwise, returns a tuple containing:
# first, the name of the corresponding method of the bot command as a string to be called by eval()
# second, the user input stripped of command word
def check_command(user_input):
	# isolate first word
	keyword = user_input.split()[0].lower()

	if keyword in BOT_COMMAND_LIST:
		# remove command word from user input
		sliced_input = re.sub(keyword, '', user_input, flags=re.IGNORECASE).strip()
		return f'{keyword}_method', sliced_input


# checks for presence of any command flags in user input
# returns a tuple containing:
# first, a dictionary of booleans indicating presence of command flags
# second, the user input stripped of flags
def check_flags(user_input):
	# insert surrounding whitespace so leading and trailing flags can still be detected
	user_input = f' {user_input} '

	# generate flag presence dictionary
	flag_presence = {flag: True if f' -{letter} ' in user_input.lower() else False for flag, letter in BOT_COMMAND_FLAGS.items()}

	# remove all 'flags', a dash followed by a single letter, even if they are not valid
	# each whitespace within input is duplicated so that all present flags can be matched by the regex properly
	user_input = re.sub(' -[a-z] ', ' ', ' ' + user_input.replace(' ', '  ') + ' ', flags=re.IGNORECASE)

	# remove excess whitespace
	user_input = ' '.join(user_input.split())

	return flag_presence, user_input


# returns page URL, comprised of sanitised search query appended to the base wiki URL
def get_appended_url(search_query):

	# symbols to ignore from user input as most of these will cause a 'Bad Title' page on the wiki
	illegal_symbols = '[+%<>|}{[\]]+'

	search_query = sub(illegal_symbols, '', search_query)

	# replace ? with %3F
	# used to be for Smoothie? but it has since changed name
	search_query = search_query.replace('?', '%3F')

	# check if 'arrows' is the last word and remove the trailing S
	if search_query.strip()[-6:].lower() == 'arrows':
		search_query = search_query[:-1]

	search_query = custom_capitalise_string(search_query)
	return f'{BASE_WIKI_URL}{search_query}'.replace(' ', '_')


# detect special smoothie type keyword in user input and remove it
# returns new search query and the smoothie type as two separate variables
# returns 'basic' by default since don't expect basic to be explicitly stated for smoothies
def detect_smoothie_type(search_query):
	smoothie_type = 'basic'

	# detect any special smoothie types from input, e.g. beefy, sticky
	# does not account for multiple smoothie types, will just take the last one iterated
	for special in SMOOTHIE_BASES:
		if special in search_query.lower():
			new_search_query = sub(special, '', search_query, flags=IGNORECASE)

			# if the input was just the smoothie type alone, do not remove it
			if new_search_query:
				search_query = new_search_query
				smoothie_type = special

	return ' '.join(search_query.split()), smoothie_type


# adds in smoothie base ingredient to dictionary of item attributes
def insert_smoothie_base(object_info, smoothie_type):
	smoothie_name = object_info['name']
	base_ingredient = SMOOTHIE_BASES[smoothie_type]
	
	if smoothie_name == DEFAULT_SMOOTHIE_NAME:
		object_info['recipe'] = {}

	object_info['recipe_name'] = f"{smoothie_type.title()} {smoothie_name}"
	object_info['recipe'][base_ingredient] = 1

	return object_info


# insert BURG.L emoji to the front of string
def prefix_burgl_emoji(input_string):
	if 'BURG.L' in CUSTOM_EMOJIS:
		return f"{CUSTOM_EMOJIS['BURG.L']} *{input_string}*"
	else:
		return f'*{input_string}*'


# returns string surrounded by double underscores, which is the syntax for underlined text on Discord
# at the same time, ensure that the whitespace in between emoji and text is not underlined
def underline_text(input_string):
	return f'__{input_string}__'.replace('> ', '>__ __')


# insert pet icon emoji behind the name of corresponding tameable creature
def append_pet_emoji(creature_name):
	if creature_name in CUSTOM_EMOJIS:
		return f'{creature_name} {CUSTOM_EMOJIS[creature_name]}'
	else:
		return creature_name


# insert elemental icon emoji behind the name of elemental weapons
def append_elem_emoji(weapon_name, elemental_type):
	if elemental_type in CUSTOM_EMOJIS:
		return f'{weapon_name} {CUSTOM_EMOJIS[elemental_type]}'
	else:
		return weapon_name


# insert corresponding custom emoji for specific attributes
def prefix_custom_emoji(input_string, is_robot=False):
	for keyword, emoji in CUSTOM_EMOJIS.items():

		# ignore creature back emoji if object is robot
		if is_robot and keyword == 'Back':
			continue

		elif is_robot and keyword == 'RobotBack':  # check if weak point is a robot's back
			input_string = input_string.replace('Back', f'{emoji} Back')

		elif isinstance(keyword, str):
			input_string = input_string.replace(keyword, f'{emoji} {keyword}')

	return input_string


# functions to convert a given string to lowercase or uppercase
# main purpose is to work with regex match objects
def convert_lowercase(string):
	if isinstance(string, Match):
		string = string[0]

	return string.lower()

def convert_uppercase(string):
	if isinstance(string, Match):
		string = string[0]

	return string.upper()


# returns string with properly capitalised words
def custom_capitalise_string(string):
	if len(string) < 2:
		return string.upper()

	# regex pattern for Ominent names like BURG.L, MIX.R, etc.
	ominent_pattern = '[a-z]+[.][a-z][^a-z]'
	string = sub(ominent_pattern, convert_uppercase, string.title() + ' ', flags=IGNORECASE)

	# regex pattern for contractions, matching the portion following the apostrophe
	contraction_pattern = "['’][a-z]+"
	string = sub(contraction_pattern, convert_lowercase, string, flags=IGNORECASE)

	for phrase in SPECIAL_WORDS:
		phrase = f' {phrase} '  # make sure the phrase is standalone and not part of a word

		# replace phrases with their proper capitalisation
		string = sub(phrase, phrase, string, flags=IGNORECASE)

	string = string.strip()
	return string[0].upper() + string[1:]


# returns ratio of similarity between two input strings
def string_similarity(a, b):
	return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# processes the many variations of (e)weakness and (e)resistance labels with a single function
# returns the specific header (out of 4 possibilities) and the processed string
def res_weak_processing(header, content):
	if 'weakness' in header:
		keyword = 'weakness'
	else:
		keyword = 'resistance'

	header = header.split(keyword)
	if header[0] == 'e':
		keyword = f'e{keyword}'

	return keyword, content.replace('-or-', '\n')


# returns a string representation of a recipe or repair cost list
def generate_recipe_string(recipe_list):
	recipe_string = ''

	for item in sorted(recipe_list.items()):
		recipe_string += f'{item[1]} {item[0]}\n'

	return recipe_string


# checks entire description of tasks in the Task Scheduler for any special words, and replaces them as such
def task_description_capitalisation(string):
	for special_word in SPECIAL_WORDS:
		if special_word.lower() in string:
			string = string.replace(special_word.lower(), special_word)

	return string
