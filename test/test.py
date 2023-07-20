import os
# import django
import json
import os
from os.path import dirname, abspath
import sys
# from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "command_centre_django_project.settings")
filePath = dirname(dirname(abspath(__file__)))
secret = os.path.join(filePath,'secret.json')

# # Read the contents of the JSON file
# with open(secret) as file:
#     database = json.load(file)

# # Extract the username, password, and database from the JSON data
# engine = database["django_database_settings"]["DATABASE_ENGINE"]
# name = database["django_database_settings"]["NAME"]
# username = database["django_database_settings"]["USER"]
# password = database["django_database_settings"]["PASSWORD"]
# host = database["django_database_settings"]["HOST"]
# port = database["django_database_settings"]["PORT"]

# settings.configure(
#     DATABASE_ENGINE = engine,
#     DATABASE_NAME = name,
#     DATABASE_USER = username,
#     DATABASE_PASSWORD = password,
#     DATABASE_HOST = host,
#     DATABASE_PORT = port,
# )

# django.setup()

ParentDirectory = dirname(dirname(abspath(__file__)))
ModuleDirectory = "command_centre_django_project/"
ModuleDirectory = os.path.join(ParentDirectory, ModuleDirectory)
sys.path.append(ModuleDirectory)

import device_scheduler.models

 




