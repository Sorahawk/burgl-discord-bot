from helper_functions import *
from secret_variables import JSON_API_KEY, SEARCH_ENGINE_ID


SIMILAR_THRESHOLD = 0.4

# returns the most likely wiki URL of the desired object
# if it cannot be located, it returns None. if Google API daily limit exceeded, it returns False
def locate_object_url(search_query):

	# sanitise input and get appended URL
	url = get_appended_url(search_query)

	# the appended URL can fail in the case of typos, shortforms, or some other syntax error in the user input
	valid = check_existing_page(url)

	# if result != False, then wiki page exists
	if valid: return url

	# if URL not correct, then use Google search to try and find the correct page
	# created a Google Programmable Search Engine that only searches within the Grounded wiki
	# also generated a Google Custom Search JSON API key that allows 100 queries a day for free
	url = f'https://www.googleapis.com/customsearch/v1?key={JSON_API_KEY}&cx={SEARCH_ENGINE_ID}&q={search_query}'

	results = requests.get(url).json()

	# check for suggested spelling by Google, in the case of typos
	if results.get('spelling') is not None:
		corrected_spelling = results['spelling']['correctedQuery']
		return locate_object_url(corrected_spelling)

	elif results.get('items') is not None:
		# Get the top result
		top_url = results['items'][0]['link']

		# check if the page title and input phrase are similar
		title = top_url.replace('https://grounded.fandom.com/wiki/', '')

		# return url if strings are similar and item page exists, otherwise return False
		if string_similarity(search_query, title) > SIMILAR_THRESHOLD and check_existing_page(top_url):
			return top_url
		else:
			return None

	# check if daily quota is exceeded
	elif results.get('error') is not None:
		if results['error']['code'] == 429:
			return False

	return None


# returns dictionary of available info extracted from infobox
def get_infobox_info(page_content):
	object_info = {}

	infobox = page_content.find_class('portable-infobox')[0]
	object_info['name'] = infobox.find_class('pi-title')[0].text_content()
	object_info['picture_url'] = list(infobox.find_class('image-thumbnail')[0].iterlinks())[0][2]

	# if infobox has tabs, e.g. smoothies, take the first one
	sections = infobox.find_class('wds-is-current')
	if sections != []:
		sections = sections[1].find_class('pi-data-value')
	else:
		sections = infobox.find_class('pi-data-value')

	# extract available info
	for section in sections:
		header = section.get('data-source')
		content = section.text_content()

		if header in ['aggression', 'tamewith', 'effectresistance', \
						'tooltype', 'augmenttype', 'damage', 'stun', 'speed', \
						'defense', 'class', 'food', 'water', 'health', \
						'species', 'gender']:
			object_info[header] = content
		elif header in ['description', 'info']:
			object_info['description'] = content
		elif header in ['category', 'subcat']:
			object_info['category'] = content
		elif header == 'loot':
			object_info[header] = content.strip().replace(') ', ')\n')
		elif header in ['eweakness', 'eweakness1']:
			object_info['eweakness'] = content.replace('-or-', ' and ')
		elif header in ['eresistance', 'eresistance1']:
			object_info['eresistance'] = content.replace('-or-', ' and ')
		elif header in ['weakness', 'weakness1']:
			object_info['weakness'] = content.replace('-or-', ' and ')
		elif header in ['resistance', 'resistance1']:
			object_info['resistance'] = content.replace('-or-', ' and ')
		elif header in ['effect', 'effect1', 'effect2', 'effect3', 'effect4', '-effect3', 'perk']:
			if 'effects' not in object_info:
				object_info['effects'] = content
			else:
				object_info['effects'] += f', {content}'

	return object_info


# returns recipe if the object's page has a recipe table, otherwise False
def get_recipe_table(page_content):
	try:
		recipe_table = page_content.get_element_by_id('Recipe').getparent().getnext().iterfind('tbody/tr/td')
		recipe_name = list(recipe_table)[0].text_content().strip()
		
	except KeyError:
		return False


# converts extracted object information into a formatted string
def format_object_info(object_info):
	formatted_string = f"**Name:** {object_info['name']}\n"

	if 'description' in object_info:
		formatted_string += f"**Description:** {object_info['description']}\n"

	# creatures
	if 'aggression' in object_info:
		# account for special case where Bee has 'NeutralAggressive'
		formatted_string += f"**Aggression:** {object_info['aggression'].replace('lA', 'l; A')}\n\n"

	## optional fields
	if 'tamewith' in object_info:
		formatted_string += f"**Tamed With:** {object_info['tamewith']}\n"
	if 'effectresistance' in object_info:
		formatted_string += f"**Resistance (Effect):** {object_info['effectresistance']}\n"
	if 'eresistance' in object_info:
		formatted_string += f"**Resistance (Elemental):** {object_info['eresistance']}\n"
	if 'resistance' in object_info:
		formatted_string += f"**Resistance (Damage):** {object_info['resistance']}\n"
	if 'eweakness' in object_info:
		formatted_string += f"**Weakness (Elemental):** __{object_info['eweakness']}__\n"
	if 'weakness' in object_info:
		formatted_string += f"**Weakness (Damage):** __{object_info['weakness']}__\n"

	if 'loot' in object_info:
		# if no optional fields, remove extra newline added from aggression
		if formatted_string[-2:] == '\n\n':
			formatted_string = formatted_string[:-1]
		formatted_string += f"\n**Loot:**\n{object_info['loot']}"


	# items
	if 'category' in object_info:
		formatted_string += f"**Category:** {object_info['category']}\n\n"

	## consumables
	if 'food' in object_info:
		formatted_string += f"**Food:** {object_info['food'].replace(')+', '); +')}\n"
	if 'water' in object_info:
		formatted_string += f"**Water:** {object_info['water']}\n"
	if 'health' in object_info:
		formatted_string += f"**Health:** {object_info['health']}\n"

	## armor
	if 'class' in object_info:
		formatted_string += f"**Armor Type:** {object_info['class']}\n"
	if 'defense' in object_info:
		formatted_string += f"**Defense:** {object_info['defense']}\n"

	## tools
	if 'tooltype' in object_info:
		formatted_string += f"**Damage Type:** {object_info['tooltype']}\n"
	if 'augmenttype' in object_info:
		formatted_string += f"**Element Type:** {object_info['augmenttype']}\n"
	if 'damage' in object_info:
		formatted_string += f"**Damage:** {prefix_zero(object_info['damage'])}\n"
	if 'stun' in object_info:
		formatted_string += f"**Stun:** {prefix_zero(object_info['stun'])}\n"
	if 'speed' in object_info:
		formatted_string += f"**Speed:** {prefix_zero(object_info['speed'])}\n"

	if 'effects' in object_info:
		formatted_string += f"**Effects:** {object_info['effects']}\n"


	# characters
	if 'species' in object_info:
		formatted_string += f"**Species:** {object_info['species']}\n"
	if 'gender' in object_info:
		formatted_string += f"**Gender:** {object_info['gender']}\n"

	return formatted_string


# retrieve details for an object
def get_object_info(search_query):
	url = locate_object_url(search_query)

	if url is None:  # unable to locate URL for item
		return 101
	elif not url:  # Google API daily resource exhausted
		return 103

	page_title, page_content = get_page_data(url)

	try:
		object_info = get_infobox_info(page_content)

		return (object_info, format_object_info(object_info))
	except:
		return (102, page_title)
