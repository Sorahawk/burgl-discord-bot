import re

from global_variables import *

from difflib import SequenceMatcher


# determines which command is being used, if any (remember that bot reads all messages)
# returns a tuple containing firstly, the name of the corresponding method of the bot command as a string to be called by eval()
# and secondly, the commandless user input
# otherwise returns None by default if no command given
def check_command(user_input):
	lowered_input = user_input.lower() + ' '

	for command_name in BOT_COMMAND_LIST:
		command = command_name + ' '

		if lowered_input.startswith(command):
			# have to slice by index instead of using replace because have to be case-insensitive
			user_input = user_input[len(command):]

			return f'{command_name}_method', user_input


# check for presence of any command flags in user input
# returns a tuple containing firstly, a dictionary of booleans indicating presence of each command flag
# and secondly, the flagless user input
def check_flags(user_input):
	flag_presence = {}

	# insert surrounding whitespace so leading and trailing flags can be detected
	user_input = f' {user_input} '

	for flag_key, flag in BOT_COMMAND_FLAGS.items():
		flag_presence[flag_key] = False
		flag = f' -{flag} '  # flag must be standalone with surrounding whitespace

		if flag in user_input.lower():
			flag_presence[flag_key] = True

		# if flag not in query, replacing won't affect the string
		user_input = user_input.replace(flag, ' ').replace(flag.upper(), ' ')

	# remove any other 'flags', a dash followed by a single letter, even if they are not valid
	other_flags = '-[a-zA-Z] '
	user_input = re.sub(other_flags, ' ', user_input + ' ')

	# remove any excess whitespace, have to be done here instead of when checking command because clean up after replacing the flags
	user_input = ' '.join(user_input.split())

	return flag_presence, user_input


# returns string with BURG.L emoji inserted to front of specified voiceline
def burgl_message(key):
	return f"{CUSTOM_EMOJIS['BURG.L']} *{BOT_VOICELINES[key]}*"


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
def prefix_emoji(input_string):
	for keyword in CUSTOM_EMOJIS:
		input_string = input_string.replace(keyword, f'{CUSTOM_EMOJIS[keyword]} {keyword}')

	return input_string


# returns string surrounded by double underscores, which is the syntax for underlined text on Discord
# at the same time, ensure that the whitespace in between emoji and text is not underlined
def underline_text(input_string):
	return f"__{input_string.replace('> ', '>__ __')}__"


# returns properly capitalised object name, accounting for names with periods, e.g. BURG.L, MIX.R
def capitalise_object_name(object_name):
	if '.' in object_name and '. ' not in object_name + ' ':  # make sure not shortform like Asst.
		object_name = object_name.upper()
	else:
		object_name = object_name.title().replace("'S", "'s")

	for phrase in SPECIAL_NAMES:
		titled_phrase = f' {phrase.title()} '  # make sure the phrase is standalone and not part of a word

		if titled_phrase in f' {object_name} ':
			object_name = object_name.replace(phrase.title(), phrase)

	return object_name.strip()


# returns page URL, comprised of sanitised search query appended to the base wiki URL
def get_appended_url(search_query):

	# symbols to ignore from user input as most of these will cause a 'Bad Title' page on the wiki
	illegal_symbols = '[\][}{><|%+]+'

	search_query = re.sub(illegal_symbols, '', search_query)

	# replace ? with %3F, e.g. Smoothie?
	search_query = search_query.replace('?', '%3F')

	# check if 'arrows' is the last word and remove the trailing S
	if search_query.strip()[-6:].lower() == 'arrows':
		search_query = search_query[:-1]

	search_query = capitalise_object_name(search_query)
	return f'{BASE_WIKI_URL}{search_query}'.replace(' ', '_')


# returns ratio of similarity between two input strings
def string_similarity(a, b):
	return SequenceMatcher(None, a.lower(), b.lower()).ratio()


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


# processes the many variations of (e)weakness and (e)resistance labels with a single function
# returns the specific header (out of 4 possibilities) and the processed string
def res_weakness_processing(header, content):
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
