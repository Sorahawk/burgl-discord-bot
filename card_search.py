from global_variables import BASE_WIKI_URL
from helper_functions import string_similarity
from url_processing import get_page_data, locate_object_url


# iterates through list of creature cards to compare the input with their names
# returns creature name and picture URL if found, otherwise error code 104
def iterate_creature_cards(search_query, creature_cards):
	highest_ratio, most_similar = 0, None

	for creature in creature_cards:
		picture_url = creature.get('href')

		# ignore gold card and creature tier images
		if 'cardgold' in picture_url.lower() or 'creaturetier' in picture_url.lower():
			continue

		creature_name = creature.getparent().text_content().strip()

		lowered_name = creature_name.lower().replace('.', '')
		lowered_query = search_query.lower().replace('.', '')
		ratio = string_similarity(lowered_name, lowered_query)

		if lowered_name == lowered_query:
			return creature_name, picture_url

		elif ratio > highest_ratio:
			highest_ratio = ratio
			most_similar = creature_name, picture_url

	if highest_ratio >= 0.5:
		return most_similar
	else:
		return 104


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

	if result is None:  # unable to locate URL
		return 104
	elif not result:  # Google API daily resource exhausted
		return 103

	search_query = result[1]
	return iterate_creature_cards(search_query, creature_cards)
