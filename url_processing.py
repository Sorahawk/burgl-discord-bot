import requests

from lxml import html
from secret_variables import JSON_API_KEY, SEARCH_ENGINE_ID
from global_variables import BASE_WIKI_URL, SIMILARITY_THRESHOLD
from helper_functions import get_appended_url, string_similarity


# returns content of wiki page as an lxml.html.HtmlElement object
def get_page_data(url, get_title=False):

	# TODO: DATABASE RETRIEVAL FOR URL->HTMLString (page html content as a string)


	html_string = requests.get(url).text

	# TODO: DATABASE INSERTION FOR URL->HTMLString (page html content as a string)


	xml_data = html.fromstring(html_string)

	page_title = xml_data.get_element_by_id('firstHeading').text_content()
	page_content = xml_data.get_element_by_id('mw-content-text')

	if get_title:
		return page_content, page_title.strip()
	
	return page_content


# returns extracted page content and title if item page exists on the wiki, otherwise returns False
def check_existing_page(url):
	page_content, page_title = get_page_data(url, True)

	try:
		# check for specific segment that says page does not exist
		invalid_text = page_content.find_class('noarticletext')
		return False
	except IndexError:  # will throw an IndexError if the item page exists
		return page_content, page_title


# returns wiki page content in a tuple (content, title)
# if URL cannot be located, returns None by default
# if Google API daily limit is exceeded, it returns False
def locate_object_url(search_query):
	url = get_appended_url(search_query)

	# the appended URL can fail in the case of typos, shortforms, or some other syntax error in the user input
	result = check_existing_page(url)

	# if result != False, wiki page exists, so return the extracted page content and title
	if result:
		return result

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
		title = top_url.replace(BASE_WIKI_URL, '')

		# return url if strings are similar and item page exists, otherwise return False
		if string_similarity(search_query, title) > SIMILARITY_THRESHOLD:
			return check_existing_page(top_url)

	# check if daily quota is exceeded
	elif results.get('error') is not None:
		if results['error']['code'] == 429:
			return False
