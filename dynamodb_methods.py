import boto3

from global_variables import DDB_TABLE_HEADERS
from secret_variables import AWS_ACCESS_KEY, AWS_SECRET_KEY


# initialises and returns DynamoDB session
def ddb_create_session():
	return boto3.resource('dynamodb', region_name='ap-southeast-1', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)


# returns tuple consisting of table key and attribute headers
def get_table_headers(table_name):
	return DDB_TABLE_HEADERS[table_name]


# inserts specified key and attribute values into specified table
# works for updating too, as entire entry will be overwritten even if that primary key already exists
def ddb_insert_item(table_name, key, attribute):
	table = ddb_create_session().Table(table_name)
	key_header, attribute_header = get_table_headers(table_name)

	try:
		table.put_item(Item={
			key_header: key,
			attribute_header: attribute})

		return True

	except:  # can fail if key input is empty
		return False


# returns entry of a specified primary key in a specified table if it exists
# otherwise, returns False
def ddb_retrieve_item(table_name, key):
	table = ddb_create_session().Table(table_name)
	key_header = get_table_headers(table_name)[0]

	response = table.get_item(Key={key_header: key})

	try:
		return response['Item']
	except KeyError:  # entry with that primary key does not exist
		return False


# returns list of dictionaries representing all entries in specified table
# if table is empty, returns an empty list
def ddb_retrieve_all(table_name):
	table = ddb_create_session().Table(table_name)
	return table.scan()['Items']


# deletes specified primary key from specified table
# does not throw any exception even if the key does not exist
def ddb_remove_item(table_name, key):
	table = ddb_create_session().Table(table_name)
	key_header = get_table_headers(table_name)[0]

	table.delete_item(Key={key_header: key})


# deletes all entries from specified table
# does not throw any exception even if table is already empty
def ddb_remove_all(table_name):
	table = ddb_create_session().Table(table_name)
	key_header = get_table_headers(table_name)[0]

	# scan has a size limit of 1MB, so repeat until it is empty
	while True:
		items = table.scan()['Items']

		print(items)

		if not items:
			break

		for item in items:
			table.delete_item(Key={
				key_header: item[key_header]})
