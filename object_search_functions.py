import requests

from lxml import html
from helper_functions import *
from secret_variables import JSON_API_KEY, SEARCH_ENGINE_ID
from global_variables import SIMILARITY_THRESHOLD, SMOOTHIE_BASES


# returns content of wiki page as an lxml.html.HtmlElement object
def get_page_data(url):
	xml_data = html.fromstring(requests.get(url).text)

	page_title = xml_data.get_element_by_id('firstHeading').text_content()
	page_content = xml_data.get_element_by_id('mw-content-text')

	return page_title.strip(), page_content


# returns True if item page exists on the wiki, otherwise returns False
def check_existing_page(url):
	page_content = get_page_data(url)[1]

	try:
		# check for specific segment that says page does not exist
		invalid_text = page_content.find_class('noarticletext')[0]
		return False
	except:
		# will throw an IndexError if the item page exists
		return True


# returns the most likely wiki URL of the desired object
# if it cannot be located, it returns None
# if Google API daily limit is exceeded, it returns False
def locate_object_url(search_query):
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
		if string_similarity(search_query, title) > SIMILARITY_THRESHOLD and check_existing_page(top_url):
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

	sections = infobox.find_class('pi-item-spacing')

	# extract available info
	for section in sections:
		header = section.get('data-source')
		content = section.text_content()

		# ignore the actual infobox headers
		if header is None or header.lower() == content.lower():
			continue

		standard_headers = ['aggression', 'tamewith', 'effectresistance', 'weakpoint', \
							'tooltype', 'augmenttype',  'class', 'food', 'water', 'health', \
							'species', 'gender']
		stat_headers = ['damage', 'stun', 'speed', 'defense', 'sturdiness', 'weight']

		if header in standard_headers:
			object_info[header] = content

		elif header in stat_headers:
			# wiki layout has something that reuses the 'weight' tag so find the one that is a float
			# some stats are also written as '.5' without the preceding zero
			# converting them to floats will solve both of the above
			try:
				object_info[header] = float(content)
			except:
				pass

		# when extracting smoothie info, content will include the header names, so have to remove 
		elif header in ['description', 'info']:
			object_info['description'] = content.replace('Description', '').strip()
		elif header in ['category', 'subcat']:
			object_info['category'] = content.replace('Category', '').strip()

		elif header == 'brokenwith':
			object_info[header] = content.replace('Harvest With', '').strip()
		elif header == 'tier':
			try:
				object_info[header] = section.getchildren()[0].get('title').replace('Tier', '').strip()
			except:
				# ignore Tier header
				pass

		elif header == 'loot':
			object_info[header] = content.strip().replace(')', ')\n').replace('\n ', '\n')

		elif 'weakness' in header or 'resistance' in header:
			header, content = weakness_resistance_processing(header, content)
			object_info[header] = content

		# armor sleek upgrade effect
		elif header == 'upgradeeffect':
			object_info['upgradeeffect'] = content

		# ignore the smoothie data fields labelled 'baseeffect'
		elif header != 'baseeffect' and ('effect' in header or header == 'perk'):
			if 'effects' not in object_info:
				# initially used a set to ignore duplicates, but it does not preserve insertion order
				object_info['effects'] = [content]
			else:
				# account for special case where Sticky Smoothie? has an additional effect
				if object_info['name'] == 'Smoothie?' and content == '+Regenerate':
					content = f'{content} (Sticky only)'

				# ignore any duplicate effects, e.g. during smoothie extraction
				if content not in object_info['effects']:
					object_info['effects'].append(content)

	return object_info


# returns object's crafting recipe as a Counter()
def get_recipe_table(page_content, object_name, smoothie_type):
	recipe_keyword = 'Recipe'

	# account for special case where upgraded Fiber Bandage has lower crafting costs
	if object_name == 'Fiber Bandage':
		recipe_keyword = 'Upgraded'

	# get the recipe table right below the Recipe header
	recipe_table = page_content.get_element_by_id(recipe_keyword).getparent().getnext().xpath('tbody/tr')
	recipe_type = recipe_table[0].xpath('th')[0].text_content().strip()

	if recipe_type == 'Item':
		recipe_number = 1
	elif recipe_type == 'Smoothie':
		recipe_number = 2

	recipe_table = recipe_table[1]
	recipe_name = recipe_table[0].text_content().strip()
	recipe_list = list(recipe_table[recipe_number].itertext())[::-1]

	# check if recipe crafts multiple of the object
	if recipe_name == object_name:
		recipe_name = ''

	recipe = compile_counter(recipe_list, recipe_type)

	# add in smoothie base to recipe
	if recipe_type == 'Smoothie':
		for base in SMOOTHIE_BASES:
			if smoothie_type == base:
				recipe_name = f'{base.title()} {object_name}'
				recipe[SMOOTHIE_BASES[base]] = 1
				break

	return recipe, recipe_name


# returns object's repair cost as a Counter()
def get_repair_cost(page_content):
	sections = page_content.iterdescendants('div')

	for section in sections:
		if section.get('data-source') == 'repair':
			repair_list = section
			break

	repair_list = list(repair_list.xpath('div')[0].itertext())[::-1]
	repair_cost = compile_counter(repair_list)
	
	return repair_cost
