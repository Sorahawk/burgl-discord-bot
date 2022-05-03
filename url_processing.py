import requests

from lxml import html
from secret_variables import JSON_API_KEY, SEARCH_ENGINE_ID
from global_variables import BASE_WIKI_URL, SIMILARITY_THRESHOLD
from helper_functions import get_appended_url, string_similarity


# returns page HTML content as a string and stores it to DynamoDB as well
def get_page_html(url):
	html_string = requests.get(url).text

	# TODO: DATABASE INSERT - URL->HTML_STRING

	return html_string


# returns content of wiki page as an lxml.html.HtmlElement object, and optionally the page title as a string
def convert_html_str(html_string, get_title):
	xml_data = html.fromstring(html_string)

	page_title = xml_data.get_element_by_id('firstHeading').text_content()
	page_content = xml_data.get_element_by_id('mw-content-text')

	if get_title:
		return page_content, page_title.strip()
	
	return page_content


# checks database for matching URL key for the corresponding HTML String, otherwise calls get_page_html to retrieve it
# returns content of wiki page as an lxml.html.HtmlElement object, and optionally the page title as a string
def get_page_data(url, get_title=True):

	# TODO: DATABASE RETRIEVAL - URL->HTML_STRING
	# if url in database:
		# html_string = retrieve()
	# else:
	html_string = get_page_html(url)

	return convert_html_str(html_string, get_title)


# returns True if item page exists on the wiki, otherwise returns False
def check_existing_page(page_content):
	try:
		# check for specific segment that says page does not exist
		invalid_text = page_content.find_class('noarticletext')[0]
		return False
	except IndexError:  # will throw an IndexError if the item page exists
		return True


# returns wiki page content in a tuple
# page URL is found either by appending the search query to the base URL, or going through Google
# if Google API daily limit exceeded, returns False, else returns None by default (URL can't be located)
def get_object_page(search_query):
	url = get_appended_url(search_query)

	# the appended URL can fail in the case of typos, shortforms, or some other syntax error in the user input
	page_content, page_title = get_page_data(url)

	# if result is True, wiki page exists, so return the extracted page content and title
	if check_existing_page(page_content):
		return page_content, page_title

	# if URL not correct, then use Google search to try and find the correct page
	# created a Google Programmable Search Engine that only searches within the Grounded wiki
	# also generated a Google Custom Search JSON API key that allows 100 queries a day for free
	pse_url = f'https://www.googleapis.com/customsearch/v1?key={JSON_API_KEY}&cx={SEARCH_ENGINE_ID}&q={search_query}'

	results = requests.get(pse_url).json()

	# check for suggested spelling by Google, in the case of typos
	if results.get('spelling') is not None:
		corrected_spelling = results['spelling']['correctedQuery']
		return get_object_page(corrected_spelling)

	elif results.get('items') is not None:
		# Get the top result
		top_url = results['items'][0]['link']

		# check if the page title and input phrase are similar
		title = top_url.replace(BASE_WIKI_URL, '')

		# return check_existing_page(url) if the strings are similar
		# which will in turn return the page content if the page exists, otherwise returns None
		if string_similarity(search_query, title) > SIMILARITY_THRESHOLD:
			page_content, page_title = get_page_data(top_url)

			if check_existing_page(page_content):
				return page_content, page_title

	# check if daily quota is exceeded
	elif results.get('error') is not None:
		if results['error']['code'] == 429:
			return False
