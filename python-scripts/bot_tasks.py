from requests import get
from random import choice
from subprocess import run
from discord.ext.tasks import loop
from steam.client import SteamClient
from discord import Activity, Streaming
from datetime import datetime, time, timedelta, timezone

from bot_messaging import *
from global_variables import *


# automatically rotate bot's Discord status every 10 minutes
@loop(minutes=10)
async def rotate_status(bot):
	activity, activity_type = choice(list(BOT_ACTIVITY_STATUSES.items()))

	if isinstance(activity_type, str):
		activity_status = Streaming(url=activity_type, name=activity)
	else:
		activity_status = Activity(type=activity_type, name=activity)

	await bot.change_presence(activity=activity_status)


# automatically clear caches once a week
tz = timezone(timedelta(hours=TIMEZONE_OFFSET))
@loop(time=time(hour=CACHE_CLEAR_HOUR, tzinfo=tz))
async def clear_cache_weekly():
	if datetime.today().weekday() == CACHE_CLEAR_DAY:
		clear_cache()
		await burgl_message('cleared', notify=True)


# checks project repository for new code
# pulls new code and restarts bot service when update is detected
@loop(minutes=1)
async def monitor_repository():
	url = 'https://api.github.com/repos/Sorahawk/burgl-discord-bot/commits'

	repository_headers = global_variables.REPOSITORY_HEADERS
	response = get(url, headers=repository_headers)

	if response.status_code == 200:
		if not repository_headers:
			etag = response.headers['ETag']
			global_variables.REPOSITORY_HEADERS['If-None-Match'] = etag

		# repository update detected
		else:
			await burgl_message('updating')

			# reset any changes that could have been made to the project folder and pull latest code
			run(f'cd {LINUX_ABSOLUTE_PATH} && git reset --hard HEAD && git pull', shell=True)

			# restart service
			run(f'sudo systemctl restart {LINUX_SERVICE_NAME}', shell=True)


# checks Steam for new activity related to store assets and development branches
# also notifies users when certain activities are detected
@loop(hours=1)
async def monitor_app_info():
	steam_timestamps = global_variables.STEAM_TIMESTAMPS

	steam_session = SteamClient()
	steam_session.anonymous_login()

	# retrieve latest app info
	app_info = steam_session.get_product_info([962130])

	steam_session.logout()

	# TODO: Log the latest time checked so can tell if the function is working
	await burgl_message('check_successful', notify=False)

	latest_assets = app_info['apps'][962130]['common']['store_asset_mtime']
	branches_info = app_info['apps'][962130]['depots']['branches']

	# populate dictionary when task is started for the first time
	if not steam_timestamps:
		global_variables.STEAM_TIMESTAMPS['asset_update'] = latest_assets

		for branch_name in branches_info:
			global_variables.STEAM_TIMESTAMPS[branch_name] = branches_info[branch_name]['timeupdated']

		return

	# check for store asset updates
	if steam_timestamps['asset_update'] != latest_assets:
		global_variables.STEAM_TIMESTAMPS['asset_update'] = latest_assets

		await burgl_message('assets_updated', notify=True)

	# check for development branch updates
	for branch_name in branches_info:
		branch_timing = branches_info[branch_name]['timeupdated']

		# notify users when entirely new branches are added
		if branch_name not in steam_timestamps:
			global_variables.STEAM_TIMESTAMPS[branch_name] = branch_timing

			await burgl_message('branch_active', replace=branch_name, notify=True)

		elif steam_timestamps[branch_name] != branch_timing:
			notify = branch_name in NOTIFY_BRANCHES
			global_variables.STEAM_TIMESTAMPS[branch_name] = branch_timing

			await burgl_message('branch_active', replace=branch_name, notify=notify)


@monitor_app_info.after_loop
async def restart_steam_monitoring():
	await burgl_message('check_failed', notify=True)

	# TODO: can restart the looping task again here? but still have to find out what is going on

	run(f'sudo systemctl restart {LINUX_SERVICE_NAME}', shell=True)
