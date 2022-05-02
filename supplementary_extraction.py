from url_processing import *
from helper_functions import iterate_creature_cards


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

			lowered_query = search_query.lower().replace(':', '')
			prefixed_queries = [lowered_query, f'+{lowered_query}', f'-{lowered_query}']

			if modifier_name.lower().replace(':', '') in prefixed_queries:
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

	page_content = get_page_data(url)
	creature_cards = page_content.find_class('image')

	# try to find the card with the original search query first
	result = iterate_creature_cards(search_query, creature_cards)

	if result != 104:
		print('first round success')
		return result[0], result[1]

	# correct any minor typos and predict any missing words in the creature's name
	result = locate_object_url(search_query)

	if not result or result is None:
		return 104

	# if result is string URL, then get the creature name from its resulting page (might have redirects, e.g. Ant Worker -> Red Ant Worker)
	if isinstance(result, str):
		search_query = check_existing_page(result)[1]
	else:  # result is tuple, get page title directly from result
		search_query = result[1]

	return iterate_creature_cards(search_query, creature_cards)
