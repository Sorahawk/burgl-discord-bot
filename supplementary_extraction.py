from url_processing import *


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


# returns creature card image URL of the specified creature
# if creature card can't be found, returns error code 104
def get_creature_card(search_query):
	url = 'https://grounded.fandom.com/wiki/Creature_Cards'

	# correct any minor typos and predict any missing words in the creature's name
	result = locate_object_url(search_query)

	# if result is string URL, then get the creature name from the end of it
	if isinstance(result, str):
		search_query_2 = check_existing_page(result)[1]
	elif isinstance(result, tuple):
		# take the page title
		search_query_2 = result[1]
	else:
		# result not found
		search_query_2 = ''

	search_queries = [search_query, search_query_2]

	page_content = get_page_data(url)
	creature_cards = page_content.find_class('image')

	for creature in creature_cards[::2]:
		creature_name = creature.getparent().text_content().strip()

		for query in search_queries:
			# remove periods because might not get it entirely correct for the robots' names
			if creature_name.lower().replace('.', '') == query.lower().replace('.', ''):
				return creature_name, creature.get('href')

	return 104
