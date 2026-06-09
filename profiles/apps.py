
from django.apps import AppConfig
from django.core.management import call_command
import os

class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles' 

    def ready(self):
        if 'DATABASE_URL' in os.environ:
            try:
                print("Running migrations automatically...")
                call_command('migrate', '--noinput')
            except Exception as e:
                print(f"Migration error: {e}")