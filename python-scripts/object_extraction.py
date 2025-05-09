from var_global import *
from url_processing import *
from string_processing import *

from collections import Counter
from re import sub


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
				modifier_info['picture_url'] = columns[0].find_class('image')[0].get('href')

				# ignore the second column under mutations, shift to the right by one
				# also remove superscript footnote text present on some mutation descriptions and sources
				remove_footnotes = '[\[].*?[\]]'

				modifier_info['description'] = sub(remove_footnotes, '', columns[1 + index].text_content()).strip()
				modifier_info['source'] = sub(remove_footnotes, '', columns[2 + index].text_content()).strip()

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

	try:
		object_info['picture_url'] = infobox.find_class('image-thumbnail')[0].find_class('image')[0].get('href')
	except:
		# some infoboxes might not have images e.g. quests
		object_info['picture_url'] = ''

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
							'species', 'gender', 'unlock', 'description+', 'effect+']
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

		elif header == 'objectives':
			objectives = section.xpath('ul')

			# check if only have a single objective
			if not objectives:
				object_info[header] = content.strip()
			else:
				output_string = ''

				objectives = objectives[0].getchildren()

				for objective in objectives:
					output_string += objective.text_content().strip() + '\n'

				object_info[header] = output_string.strip()

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
def get_armor_pieces(page_content):
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


# matches user input to an armor set and returns it
# if no match found, returns None by default
def match_armor_set(search_query):
	search_query = search_query.lower()

	# retrieve list of all armor sets
	armor_set_list = get_all_armor_sets()

	for armor_set in armor_set_list:
		# check if armor name prefix is in search query
		if armor_set.lower() in search_query:
			return armor_set


# matches user input to an armor piece in the given armor set and returns a tuple 
# first item is name of queried armor piece, and second is type of armor piece
# if no matching piece can be found, returns None by default
def match_armor_piece(search_query, queried_set, armor_pieces):

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
def get_armor_piece_info(search_query, queried_set):

	## determine queried armor piece
	# get corresponding armor set page URL
	url = get_appended_url(f'{queried_set} Armor')
	page_content = get_page_data(url)

	# get the names of each armor piece in the set
	armor_pieces = get_armor_pieces(page_content)

	queried_piece = match_armor_piece(search_query, queried_set, armor_pieces)

	if not queried_piece:
		# no matching armor piece found
		return None

	## extract information for queried armor piece
	# initialise item_info dictionary
	item_info = {'page_url': url}
	item_info['name'], piece_type = queried_piece

	# get entire armor wikitable element
	armor_table = page_content.find_class('wikitable')

	# iterate through all tables and search for the one with the self-link header
	# prefer not to hardcode position via index in case of any future drastic page layout changes
	for table in armor_table:
		if table.find_class('mw-selflink'):
			armor_table = table
			break

	# extract common info fields
	item_info = get_shared_set_info(armor_table, item_info)

	# extract data specific to armor piece type
	item_info = get_specific_piece_info(armor_table, piece_type, item_info)

	# get corresponding crafting recipe
	item_info['recipe_name'], item_info['recipe'] = get_recipe_tables(page_content, item_info['name'])[0]

	return item_info


# updates item info dictionary with data that is common across the entire armor set
def get_shared_set_info(armor_table, item_info):

	# extract armor set tier
	tier_image = armor_table.find_class('mw-selflink')[0].getprevious()

	if tier_image is not None:  # might be None, e.g. Clover Armor Set is tier-less
		item_info['tier'] = tier_image.get('title').replace('Tier', '').strip()

	# get list of row elements
	row_list = armor_table.xpath('tbody/tr')

	# extract armor class
	class_row = row_list[-1]
	item_info['class'] = list(class_row.iterdescendants('a'))[0].get('title')

	# extract effects
	effects_row = row_list[-2]
	effects_list = []

	for effect in effects_row.iterdescendants('a'):
		effect = effect.text_content().strip()

		if effect:
			effects_list.append(effect)

	item_info['effects'] = effects_list[0]
	item_info['upgradeeffect'] = effects_list[1]
	item_info['setbonus'] = effects_list[2]

	return item_info


# updates item info dictionary with data that is specific to that armor piece
def get_specific_piece_info(armor_table, piece_type, item_info):

	# set index offset based on armor piece type
	if piece_type == 'Head':
		index_offset = 0
	elif piece_type == 'Upper Body':
		index_offset = 2
	elif piece_type == 'Lower Body':
		index_offset = 4

	# insert category
	item_info['category'] = f'Armor - {piece_type}'

	# get list of specific rows
	piece_rows = armor_table.xpath('tbody/tr')[2:4]

	# extract picture URL from first column
	item_info['picture_url'] = piece_rows[0].xpath('td')[index_offset].find_class('image')[0].get('href')

	# extract defense and resistance
	stat_list = list(piece_rows[0].xpath('td')[index_offset].itertext())

	item_info['defense'] = stat_list[2]
	item_info['resistance'] = stat_list[4]

	# extract description
	item_info['description'] = piece_rows[0].xpath('td')[index_offset + 1].find('p').text_content().strip()

	# extract repair cost
	repair_list = list(piece_rows[1].xpath('td')[index_offset // 2].find('p').itertext())[::-1]
	item_info['repair_cost'] = compile_counter(repair_list)

	return item_info
