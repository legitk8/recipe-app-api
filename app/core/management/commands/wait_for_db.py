"""
Django command to wait for the database to be available.
"""
import time

from psycopg2 import OperationalError as Psycopg2OperationalError

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError


class Command(BaseCommand):
    """
        Django command to wait for database to be available.
    """
    def handle(self, *args, **options):
        """Entry point for the command."""
        self.stdout.write('Waiting for database...')
        is_db_available = False

        while not is_db_available:
            try:
                self.check(databases=['default'])
                is_db_available = True
            except (OperationalError, Psycopg2OperationalError):
                self.stdout.write('Database unavailable, sleeping for 1s...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
