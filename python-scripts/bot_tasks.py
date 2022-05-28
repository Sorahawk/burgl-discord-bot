import requests, subprocess

from random import choice
from discord.ext import tasks
from discord import Activity, Streaming
from datetime import datetime, time, timedelta, timezone

from global_variables import *


# automatically rotate bot's Discord status every 10 minutes
@tasks.loop(minutes=10)
async def rotate_status(bot):
	activity, activity_type = choice(list(BOT_ACTIVITY_STATUSES.items()))

	if isinstance(activity_type, str):
		activity_status = Streaming(url=activity_type, name=activity)
	else:
		activity_status = Activity(type=activity_type, name=activity)

	await bot.change_presence(activity=activity_status)


# automatically clear caches once a week
timezone = timezone(timedelta(hours=TIMEZONE_OFFSET))
@tasks.loop(time=time(hour=CACHE_CLEAR_HOUR, tzinfo=timezone))
async def clear_cache_weekly():
	if datetime.today().weekday() == CACHE_CLEAR_DAY:
		clear_cache()
		await burgl_message('cleared')


# initialise persistent header variable to store latest HTTP response ETag
stored_headers = {}

# checks project repository for new code every minute
# pulls new code and restarts bot service when update is detected
@tasks.loop(minutes=1)
async def monitor_repository():
	url = 'https://api.github.com/repos/Sorahawk/burgl-discord-bot/commits'
	response = requests.get(url, headers=stored_headers)

	if response.status_code == 200:
		if not stored_headers:
			etag = response.headers['ETag']
			stored_headers['If-None-Match'] = etag

		# new repository update
		else:
			await burgl_message('updating')

			# pull latest code and restart service
			subprocess.run(f'cd {LINUX_ABSOLUTE_PATH} && git pull && sudo systemctl restart {LINUX_SERVICE_NAME}', shell=True)
