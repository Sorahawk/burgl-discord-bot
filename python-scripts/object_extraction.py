from url_processing import *
from global_constants import *
from string_processing import *

from collections import Counter


# returns dictionary of extracted information for a given status effect or mutation
# if modifier can't be found, returns None by default
def get_modifier_info(search_query):
	urls = [f'{BASE_WIKI_URL}Status_Effects', f'{BASE_WIKI_URL}Mutations']

	modifier_info = {}

	for index in range(len(urls)):
		page_content = get_page_data(urls[index])
		modifier_list = page_content.xpath('div/table/tbody/tr')

		for modifier in modifier_list:
			columns = modifier.getchildren()

			# remove superscript footnote text present on some mutation names
			modifier_name = columns[0].text_content().split('[')[0].strip()

			if modifier_name == 'Effect' or modifier_name == 'Mutation':
				continue

			lowered_query = search_query.lower().replace(':', '')
			prefixed_queries = [lowered_query, f'+{lowered_query}', f'-{lowered_query}']

			if modifier_name.lower().replace(':', '') in prefixed_queries:
				modifier_info['name'] = modifier_name
				modifier_info['picture_url'] = list(columns[0].iterlinks())[0][2]

				# ignore the second column under mutations, shift to the right by one
				# also remove superscript footnote text present on some mutation descriptions and sources
				modifier_info['description'] = columns[1 + index].text_content().split('[')[0].replace('\n\n', '\n').strip()
				modifier_info['source'] = columns[2 + index].text_content().split('[')[0].strip()

				# replace source text for purchasable mutations
				if 'BURG.L' in modifier_info['source']:
					modifier_info['source'] = 'Purchase from BURG.L'

				# insert wiki URL depending on whether modifier is status effect or mutation
				modifier_info['page_url'] = urls[index]
				return modifier_info


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

		if header is None:
			continue

		# ignore actual infobox headers
		elif content == 'Effect' or header.lower() == content.lower():
			continue

		standard_headers = ['aggression', 'tamewith', 'immune', 'weakpoint',
							'tooltype', 'augmenttype',  'class', 'water', 'health',
							'species', 'gender', 'description+', 'effect+']
		stat_headers = ['damage', 'stun', 'speed', 'defense', 'sturdiness', 'weight']

		if header in standard_headers:
			object_info[header] = content

		elif header in stat_headers:
			# for base building parts, wiki layout has some text stuff that incorrectly reuses the 'weight' label
			# some item stats are also written as '.5' without the preceding zero
			# converting them to floats will solve both of the above
			try:
				object_info[header] = float(content)
			except:
				pass

		# when extracting smoothie info, content will include the header names, so have to remove 
		elif header in ['description', 'info']:
			object_info['description'] = content.replace('Description', '').strip()
		elif header in ['category', 'subcat', 'type']:
			object_info['category'] = content.replace('Category', '').strip()

		elif header == 'brokenwith':
			section = section.xpath('div')[0]
			content = section.text_content().strip()

			images = section.find_class('image')

			for image in images:
				image_name = image.getchildren()[0].get('data-image-name').split('.')[0].lower()

				if 'tier' in image_name:
					content += f" (Tier {image_name.replace('tier', '')})"
					break

			object_info[header] = content

		elif header in ['tier', 'tier+']:
			try:
				object_info[header] = section.getchildren()[0].get('title').replace('Tier', '').strip()
			except:
				# ignore Tier header
				pass

		elif header == 'loot':
			object_info[header] = content.strip().replace(')', ')\n').replace('\n ', '\n')

		# account for special cases of food with Fresh versions
		elif header == 'food':
			object_info[header] = content.strip().replace(')+', ')\n+')

		elif 'weakness' in header or 'resistance' in header:
			header, content = res_weak_processing(header, content)
			object_info[header] = content

		# armor sleek upgrade effect
		elif 'upgradeeffect' in header:
			object_info['upgradeeffect'] = content

		# ignore the smoothie data fields labelled 'baseeffect'
		elif header != 'baseeffect' and ('effect' in header or header == 'perk'):
			if 'effects' not in object_info:
				# initially used a set to ignore duplicates, but it does not preserve insertion order
				object_info['effects'] = [content]
			else:
				# account for special case where Sticky default smoothie has an additional effect
				if object_info['name'] == DEFAULT_SMOOTHIE_NAME and content == '+Regenerate':
					content = f'{content} (Sticky only)'

				# ignore any duplicate effects, e.g. during smoothie extraction
				if content not in object_info['effects']:
					object_info['effects'].append(content)

	# if present, convert effects list into a string
	if 'effects' in object_info:
		object_info['effects'] = '\n'.join(object_info['effects'])

	return object_info


# returns object's crafting recipe(s) as a list of tuples
# first entry of the tuple is the recipe name while second entry is the recipe as a Counter()
def get_recipe_tables(page_content, object_name):
	# get all tables on the page
	table_list = page_content.find_class('wikitable')

	full_recipe_list = []

	for table in table_list:

		# check first column to determine whether that recipe table is for that object
		# by either checking for a self-link (for most objects)
		# or comparing the actual object name (for armor pieces within armor sets)
		first_column = table.xpath('tbody/tr/td')[0]

		if first_column.find_class('mw-selflink') or object_name == first_column.text_content().strip():
			recipe_info = process_recipe(table.xpath('tbody/tr'), object_name)

			full_recipe_list.append(recipe_info)

	return full_recipe_list


# processes recipe table and extracts crafting information
def process_recipe(recipe_table, object_name):
	recipe_type = recipe_table[0].xpath('th')[0].text_content().strip()

	if recipe_type == 'Item':
		recipe_number = 1
	elif recipe_type == 'Smoothie':
		recipe_number = 2

	recipe_table = recipe_table[1]

	# check if recipe crafts multiple of the object
	recipe_name = recipe_table[0].text_content().strip()

	if recipe_name == object_name:
		recipe_name = ''

	# extract recipe and consolidate into a Counter()
	recipe_list = list(recipe_table[recipe_number].itertext())[::-1]

	recipe = compile_counter(recipe_list, recipe_type)

	return recipe_name, recipe


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


# returns a Counter() of the compiled materials and their quantities
# collections.Counter will make it much easier to recursively sum up materials for Chopping List in future
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


# returns a list of all armor sets, extracted from the overall Armor page
def get_all_armor_sets():
	url = f'{BASE_WIKI_URL}Armor'

	page_content = get_page_data(url)
	page_content = page_content.find_class('tocsection-1')[0].xpath('ul')[0].find_class('toctext')

	armor_set_list = []

	for armor in page_content:
		# remove 'Armor Set' suffix from each name
		armor_set_list.append(armor.text_content().replace('Armor Set', '').strip())

	return armor_set_list


# returns a list of each armor piece in the queried set
def get_armor_set(page_content):
	table_list = page_content.find_class('wikitable')

	armor_types = ['Head', 'Upper Body', 'Lower Body']
	armor_pieces = {}

	for table in table_list:
		# skip table if it's not a recipe
		if table.xpath('tbody/tr/th')[0].text_content().strip() != 'Item':
			continue

		first_column = table.xpath('tbody/tr/td')[0]

		piece_type = armor_types.pop(0)
		armor_pieces[piece_type] = first_column.text_content().strip()

	return armor_pieces


# matches user input to an armor piece in the given armor set and returns a tuple 
# first item is name of queried armor piece, and second is type of armor piece
# if no matching piece can be found, returns None by default
def process_armor_input(search_query, queried_set, armor_pieces):

	# compare search query against armor piece names
	for piece_type, full_name in armor_pieces.items():
		short_name = full_name.replace(queried_set, '').strip()

		if short_name.lower() in search_query:
			return full_name, piece_type

	# if no armor piece names are matched, then cross-check with ARMOR_KEYWORDS
	for piece_type, keywords in ARMOR_KEYWORDS.items():
		for word in keywords:
			if word in search_query:
				return armor_pieces[piece_type], piece_type


# returns dictionary of extracted information for a piece of armor within a full set
# if no matching armor piece can be found, returns None by default
def get_armor_piece_info(search_query):

	## determine queried armor set

	search_query = search_query.lower()
	queried_set = None

	# retrieve list of all armor sets
	armor_set_list = get_all_armor_sets()

	for armor_set in armor_set_list:
		# check if armor name prefix is in search query
		if armor_set.lower() in search_query:
			queried_set = armor_set
			break

	if not queried_set:
		# no matching armor set found
		return None

	## determine queried armor piece

	# get corresponding armor set page URL
	url = get_appended_url(f'{queried_set} Armor')
	page_content = get_page_data(url)

	# get the names of each armor piece in the set
	armor_pieces = get_armor_set(page_content)

	queried_piece = process_armor_input(search_query, queried_set, armor_pieces)

	if not queried_piece:
		# no matching armor piece found
		return None

	## extract information for matched armor piece

	item_info = {'page_url': url}

	item_info['name'], piece_type = queried_piece
	item_info['recipe_name'], item_info['recipe'] = get_recipe_tables(page_content, item_info['name'])[0]

	item_info = get_shared_set_info(page_content, item_info)

	return item_info


# 
def get_shared_set_info(page_content, item_info):
	set_table = page_content.find_class('mw-selflink')[0].getparent().getparent().itersiblings()
	set_table = list(set_table)
	#print(set_table)





#print(get_armor_piece_info('ladybug hat'))
