<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Sorahawk/BURG.L_Discord_Bot">
    <img src="images/logo.jpg" alt="Logo" width="225" height="200">
  </a>
  <h3 align="center">BURG.L Discord Bot</h3>
  <p align="center">
    A Discord resource management bot that augments the Grounded gaming experience.
  </p>
</div>



# About The Project

The BURG.L Discord Bot is a resource manager that aids [Grounded](https://grounded.obsidian.net/) players by tracking requirements and allocating tasks. BURG.L pulls data from the [Grounded Wiki](https://grounded.fandom.com/wiki/Grounded_Wiki) to get information for items, such as crafting costs. Despite the recent introduction of slash commands by Discord, prefix commands are still used in this project as Discord's in-game overlay does not work with slash commands.

The overall roadmap and development tracker for this project can be found on Trello: [BURG.L Discord Bot - Roadmap and Task Tracker](https://trello.com/b/nBXnpnol/burgl-discord-bot-roadmap-and-task-tracker/).


## Planned Features

| Feature | Description |
| ------- | ----------- |
| Object Search | Retrieves object information (e.g. creatures, items, resources, status effects, mutations) |
| Creature Card Search | Retrieves a creature's bestiary card |
| Chopping List | Consolidates total number of resources required for crafting and building. |
| Task Scheduler | Keeps track of user-inputted tasks, as well as generating harvesting tasks based on the Chopping List |
| Database Storage and Caching | Stores permanent data, as well as caching queried data from searches |


## Built With

* [Amazon DynamoDB](https://aws.amazon.com/dynamodb/)
* [Amazon EC2](https://aws.amazon.com/ec2/)
* [Custom Search JSON API by Google](https://developers.google.com/custom-search/v1/introduction)
* [Discord.py](https://discordpy.readthedocs.io/)
* [Programmable Search Engine by Google](https://programmablesearchengine.google.com/)
* [Python](https://www.python.org/)



# Usage

## Bot Commands

* `.help` - Displays help message.
* `.search <object_name>` - Displays any available details of the object, including its picture and description.
    * _This search works with any Grounded wiki page with an infobox, e.g. creatures, equipment, resources, building components, resource nodes, landmarks._
    * _Use flag `-m` to search for status effects and mutations._
    * _Use flag `-f` to force the search to bypass any binded shortcuts._
* `.card <creature_name>` - Displays the specified creature's bestiary card.
    * _Use flag `-f` to force the search to bypass any binded shortcuts._
* `.bind <full_object_name>, <shortcut_1>, <shortcut_2>, ...` - Binds one or more shortcut phrases to a full object name.
    * _Each parameter is case-insensitive and must be separated by a comma._
* `.purge` - Purges the webpage data and object information caches.


## Error Codes

| Code | Description |
| ---- | ----------- |
| 101 | Wiki page for the object cannot be located. |
| 102 | Wiki page for the object has an unsupported layout. |
| 103 | Daily limit of 100 queries for Google Custom Search JSON API has been exceeded. |
| 104 | Bestiary card for the creature cannot be located. |

---

Copyright © 2022, [Sorahawk](https://github.com/Sorahawk)
