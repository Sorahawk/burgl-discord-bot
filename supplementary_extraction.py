from url_processing import *
from global_variables import BASE_WIKI_URL
from helper_functions import iterate_creature_cards


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
	url = f'{BASE_WIKI_URL}Creature_Cards'

	page_content = get_page_data(url)
	creature_cards = page_content.find_class('image')

	# try to find the card with the original search query first
	result = iterate_creature_cards(search_query, creature_cards)

	if result != 104:
		return result[0], result[1]

	# correct any minor typos and predict any missing words in the creature's name
	result = locate_object_url(search_query)

	if not result:  # if result is False or None
		return 104

	search_query = result[1]
	return iterate_creature_cards(search_query, creature_cards)
