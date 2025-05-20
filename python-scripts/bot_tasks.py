import var_global, requests

from var_global import *
from bot_messaging import *

from random import choice
from subprocess import run
from discord.ext.tasks import loop
from discord import Activity, Streaming
from datetime import datetime, time, timedelta, timezone


# automatically rotate bot's Discord status every 10 minutes
@loop(minutes=10)
async def rotate_status():
	activity, activity_type = choice(list(BOT_ACTIVITY_STATUSES.items()))

	if isinstance(activity_type, str):
		activity_status = Streaming(url=activity_type, name=activity)
	else:
		activity_status = Activity(type=activity_type, name=activity)

	await var_global.BOT_INSTANCE.change_presence(activity=activity_status)


'''
# automatically clear caches once a week
tz = timezone(timedelta(hours=TIMEZONE_OFFSET))
@loop(time=time(hour=CACHE_CLEAR_HOUR, tzinfo=tz))
async def clear_cache_weekly():
	if datetime.today().weekday() == CACHE_CLEAR_DAY:
		clear_cache()
		await burgl_message('cleared', notify=True)
'''


# checks project repository for new code
# pulls new code and restarts bot service when update is detected
@loop(minutes=3)
async def monitor_repository():
	table_name = MISC_TABLE
	key = 'Repository_ETag'
	repository_headers = var_global.REPOSITORY_HEADERS

	# check repository status
	response = requests.get(REPOSITORY_URL, headers=repository_headers)

	# if response status code is not 200, means etag is the same as the one provided in the request
	if response.status_code != 200:
		return

	etag = response.headers['ETag']

	# if global header dictionary empty, means the task is running for first time upon initialisation
	if not repository_headers:
		# check storage for latest etag value, if any
		result = ddb_retrieve_item(table_name, key)
		value_header = get_table_headers(table_name)[1]

		# if etag exists in storage, and is same as response etag, update local header and return
		if result and result[value_header] == etag:
			var_global.REPOSITORY_HEADERS['If-None-Match'] = etag
			return

	# if one of the following conditions are fulfilled:
	# 1) global headers not empty
	# 2) global headers empty, but no existing etag in storage
	# 3) global headers empty and storage has existing etag, but different value
	# then update storage with latest etag, pull latest code and restart bot
	
	await burgl_message('updating')

	# write latest etag value to persistent storage 
	ddb_insert_item(table_name, key, etag)

	# reset any changes that could have been made to the project folder and pull latest code
	run(f"cd {LINUX_ABSOLUTE_PATH} && git reset --hard HEAD && git pull", shell=True)

	# restart service
	run(['sudo', 'systemctl', 'restart', LINUX_SERVICE_NAME])


# checks Steam for new activity related to store assets and development branches
# also notifies users when certain activities are detected
@loop(minutes=13)
async def monitor_app_info():
	table_name = MISC_TABLE
	key = 'Steam_Timestamps'
	steam_timestamps = var_global.STEAM_TIMESTAMPS
	changes_detected = False

	try:
		response = requests.get('https://api.steamcmd.net/v1/info/962130', timeout=10)

		# ensure that response is valid and contains requested info
		if response.status_code != 200:
			return var_global.OPERATIONS_LOG.warning(response)

	# as the SteamCMD API is third-party and is not as established as something like GitHub,
	# have to account for possible timeout resulting from API overload, as well as other unexpected errors
	except Exception as e:
		return var_global.OPERATIONS_LOG.warning(e)

	app_info = response.json()['data']['962130']
	latest_assets = app_info['common']['store_asset_mtime']
	branches_info = app_info['depots']['branches']

	# if global timestamp dictionary empty, means the task is running for first time upon initialisation
	if not steam_timestamps:
		# retrieve timestamps from storage for latest values, if any
		result = ddb_retrieve_item(table_name, key)
		value_header = get_table_headers(table_name)[1]

		# if values are present in storage, update timestamps with latest for each category
		if result:
			result = result[value_header]

			for category in result:
				var_global.STEAM_TIMESTAMPS[category] = result[category]

		else:  # populate global dictionary and update persistent storage
			changes_detected = True

			var_global.STEAM_TIMESTAMPS['asset_update'] = latest_assets

			for branch_name in branches_info:
				var_global.STEAM_TIMESTAMPS[branch_name] = branches_info[branch_name]['timeupdated']

	# check for store asset updates
	if steam_timestamps['asset_update'] != latest_assets:
		changes_detected = True

		var_global.STEAM_TIMESTAMPS['asset_update'] = latest_assets

		await burgl_message('assets_updated', notify=True)

	# check for development branch updates
	for branch_name in branches_info:
		branch_timing = branches_info[branch_name]['timeupdated']

		# notify users when entirely new branches are added
		if branch_name not in steam_timestamps:
			changes_detected = True

			var_global.STEAM_TIMESTAMPS[branch_name] = branch_timing

			await burgl_message('branch_active', replace=branch_name, notify=True)

		elif steam_timestamps[branch_name] != branch_timing:
			changes_detected = True

			notify = branch_name in NOTIFY_BRANCHES
			var_global.STEAM_TIMESTAMPS[branch_name] = branch_timing

			await burgl_message('branch_active', replace=branch_name, notify=notify)

	# write latest timestamps to persistent storage 
	if changes_detected:
		ddb_insert_item(table_name, key, var_global.STEAM_TIMESTAMPS)
