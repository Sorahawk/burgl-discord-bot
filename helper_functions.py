import re, requests, string

from lxml import html
from difflib import SequenceMatcher


# returns True if item page exists on the wiki, otherwise returns False
def check_existing_page(url):
	page_content = get_page_data(url)[1]

	try:
		# check for specific segment that says page does not exist
		invalid_text = page_content.find_class('noarticletext')[0]
		return False
	except:
		# will throw an IndexError if the item page exists
		return True


# sanitises search query and appends it to base wiki URL, and returns result 
def get_appended_url(search_query):

	# sanitise input as these symbols will cause a 'Bad Title' page on the wiki
	illegal_symbols = '[\][}{><|%+]+'
	search_query = re.sub(illegal_symbols, '', search_query)

	# replace ? with %3F
	search_query = search_query.replace('?', '%3F')

	# check if 'arrows' is the last word and remove the trailing S
	if search_query.strip()[-6:].lower() == 'arrows':
		search_query = search_query[:-1]

	# capitalise the first letter of every word as the webpage URL is case sensitive
	# initially used .title() but then realised that it also capitalises the letter after an apostrophe
	return f'https://grounded.fandom.com/wiki/{string.capwords(search_query)}'


# returns content of wiki page as an lxml.html.HtmlElement object
def get_page_data(url):
	xml_data = html.fromstring(requests.get(url).text)

	page_title = xml_data.get_element_by_id('firstHeading').text_content()
	page_content = xml_data.get_element_by_id('mw-content-text')

	return page_title.strip(), page_content


# prefix a 0 if stat is just '.5'
def prefix_zero(content):
	if content == '.5':
		content = f'0{content}'
	return content


# returns ratio of similarity between two input strings
def string_similarity(a, b):
	return SequenceMatcher(None, a.lower(), b.lower()).ratio()
