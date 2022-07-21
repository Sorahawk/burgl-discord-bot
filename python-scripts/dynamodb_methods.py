from secrets import *
from global_constants import *

from boto3 import resource


# initialises and returns DynamoDB session
def create_ddb_session():
	return resource('dynamodb', region_name=AWS_REGION_NAME, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)


# returns tuple consisting of table key and attribute headers
def get_table_headers(table_name):
	return TABLE_HEADERS[table_name]


# inserts specified key and attribute values into specified table
# works for updating too, as entire entry will be overwritten even if that primary key already exists
def ddb_insert_item(table_name, key, attributes):
	table = create_ddb_session().Table(table_name)
	key_header, attribute_headers = get_table_headers(table_name)

	if isinstance(attribute_headers, str):
		attributes = (attributes, )
		attribute_headers = (attribute_headers, )

	output_dict = {key_header: key}

	for index in range(len(attribute_headers)):
		header = attribute_headers[index]
		output_dict[header] = attributes[index]

	try:
		table.put_item(Item=output_dict)
		return True

	except:  # can fail if key input is empty
		return False


# returns entry of a specified primary key in a specified table if it exists
# otherwise, returns False
def ddb_retrieve_item(table_name, key):
	table = create_ddb_session().Table(table_name)
	key_header = get_table_headers(table_name)[0]

	response = table.get_item(Key={key_header: key})

	try:
		return response['Item']
	except KeyError:  # entry with that primary key does not exist
		return False


# returns list of dictionaries representing all entries in specified table
# scan() has a size limit of 1MB
# if table is empty, returns an empty list
def ddb_retrieve_all(table_name):
	table = create_ddb_session().Table(table_name)
	return table.scan()['Items']


# deletes specified primary key from specified table
# does not throw any exception even if the key does not exist, but will throw if key input is empty
def ddb_remove_item(table_name, key):
	table = create_ddb_session().Table(table_name)
	key_header = get_table_headers(table_name)[0]

	try:
		return table.delete_item(Key={key_header: key}, ReturnValues='ALL_OLD')

	except:  # can fail if key input is empty
		return False


# deletes all entries from specified table
# does not throw any exception even if table is already empty
def ddb_remove_all(table_name):
	table = create_ddb_session().Table(table_name)
	key_header = get_table_headers(table_name)[0]

	# scan() has a size limit of 1MB, so repeat until it is empty
	while True:
		items = table.scan()['Items']

		if not items:
			break

		for item in items:
			table.delete_item(Key={key_header: item[key_header]})
