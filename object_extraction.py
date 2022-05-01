from url_processing import get_page_data
from global_variables import SMOOTHIE_BASES
from helper_functions import weakness_resistance_processing, compile_counter


# returns dictionary of extracted information for a given status effect or mutation
# if modifier can't be found, returns None by default
def get_modifier_info(search_query):
	urls = ['https://grounded.fandom.com/wiki/Status_Effects', 'https://grounded.fandom.com/wiki/Mutations']

	modifier_info = {}

	for index in range(len(urls)):
		page_content = get_page_data(urls[index])
		modifier_list = page_content.xpath('div/table/tbody/tr')

		for modifier in modifier_list:
			columns = modifier.getchildren()

			# remove superscript footnote text from some mutation names
			modifier_name = columns[0].text_content().strip().split('[')[0]

			if modifier_name == 'Effect' or modifier_name == 'Mutation':
				continue

			lowered_query = search_query.lower()
			prefixed_queries = [lowered_query, f'+{lowered_query}', f'-{lowered_query}']

			if modifier_name.lower() in prefixed_queries:
				modifier_info['name'] = modifier_name
				modifier_info['picture_url'] = list(columns[0].iterlinks())[0][2]

				# ignore the second column under mutations, shift to the right by one
				modifier_info['description'] = columns[1 + index].text_content().strip().replace('\n\n', '\n')
				modifier_info['source'] = columns[2 + index].text_content().strip()

				# replace source text for purchasable mutations
				if 'BURG.L' in modifier_info['source']:
					modifier_info['source'] = 'Purchase from BURG.L'

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

		standard_headers = ['aggression', 'tamewith', 'effectresistance', 'weakpoint', \
							'tooltype', 'augmenttype',  'class', 'food', 'water', 'health', \
							'species', 'gender']
		stat_headers = ['damage', 'stun', 'speed', 'defense', 'sturdiness', 'weight']

		if header in standard_headers:
			object_info[header] = content

		elif header in stat_headers:
			# for base building parts, wiki layout has things that incorrectly reuse the 'weight' label
			# some item stats are also written as '.5' without the preceding zero
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
		elif 'upgradeeffect' in header:
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
