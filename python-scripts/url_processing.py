import requests  # don't import requests.get directly to avoid confusion as get() is a common function name

from var_secret import *
from var_global import *
from dynamodb_methods import *
from storage_functions import *
from string_processing import *

from lxml import html


# returns content of wiki page as an lxml.html.HtmlElement object
def get_page_data(wiki_url, get_title=False):

	# many search queries can refer to the same object, thus caching the page HTML itself helps to speed up response times
	# check if HTML of the wiki page has already been cached
	html_string = retrieve_from_cache(HTML_TABLE, wiki_url)

	if not html_string:
		# retrieve page HTML
		html_string = requests.get(wiki_url).text

		# cut out massive redundant parts of the page HTML to save on DynamoDB read/write units
		html_string = html_string.split('page-header__title-wrapper">')[1]  # slice off unnecessary headers up till page title
		html_string = html_string.split('<table cellspacing="0" class="navbox"')[0]  # slice off everything after unique page content ends
		html_string = html_string.split('<div class="page-footer')[0]  # slice off footer for pages which don't have the navbox used above

		# cache shortened page HTML
		if not DEBUG_MODE:
			ddb_insert_item(HTML_TABLE, wiki_url, html_string)

	xml_data = html.fromstring(html_string)

	page_title = xml_data.get_element_by_id('firstHeading').text_content()
	page_content = xml_data.get_element_by_id('mw-content-text')

	if get_title:
		return page_content, page_title.strip()
	else:
		return page_content


# returns extracted page content and title if item page exists on the wiki, otherwise returns None by default
def check_existing_page(wiki_url):
	page_content, page_title = get_page_data(wiki_url, True)

	# check for specific segment that says page does not exist
	invalid_text = page_content.find_class('noarticletext')

	if not invalid_text:
		return page_content, page_title


# returns wiki page content in a tuple (content, title, url)
# if URL cannot be located, returns None by default
# if Google API daily limit is exceeded, it returns False
def locate_object_url(search_query):
	url = get_appended_url(search_query)

	# the appended URL can fail in the case of typos, nicknames, or some other syntax error in the user input
	result = check_existing_page(url)

	# if wiki page exists, return the extracted page content and title
	if result:
		return result[0], result[1], url

	# if URL not correct, then use Google search to try and find the correct page
	# created a Google Programmable Search Engine that only searches within the Grounded wiki
	# also generated a Google Custom Search JSON API key that allows 100 queries a day for free
	url = f"https://www.googleapis.com/customsearch/v1?key={JSON_API_KEY}&cx={SEARCH_ENGINE_ID}&q={search_query}"

	results = requests.get(url).json()

	# check for suggested spelling by Google, in the case of typos
	if 'spelling' in results:
		corrected_spelling = results['spelling']['correctedQuery']
		return locate_object_url(corrected_spelling)

	elif 'items' in results:
		# Get the top result
		top_url = results['items'][0]['link']

		# check if the page title and input phrase are similar
		title = top_url.replace(BASE_WIKI_URL, '')

		# return url if strings are similar and item page exists, otherwise return False
		if string_similarity(search_query, title) > SIMILAR_THRESHOLD_API:
			result = check_existing_page(top_url)

			if result:
				return result[0], result[1], top_url
			else:
				return result

	# check if daily quota is exceeded
	elif 'error' in results:
		if results['error']['code'] == 429:
			return False
