#!/usr/bin/env python
import os
from pathlib import Path

from django.conf import settings
from django.core import management
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

settings.configure(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "PASSWORD": os.environ["DB_PASSWORD"],
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "HOST": os.environ["DB_HOST"],
            "PORT": "5432",
        }
    },
    INSTALLED_APPS=["app.application"],
)

if __name__ == "__main__":
    management.execute_from_command_line()
