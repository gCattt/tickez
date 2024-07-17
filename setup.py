import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tickez.settings")
django.setup()

from tickez.initcmds import init_db, erase_db

if __name__ == "__main__":
    erase_db()
    init_db()