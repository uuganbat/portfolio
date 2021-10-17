# -*- coding:utf-8 -*-

import os

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from django.db import DEFAULT_DB_ALIAS, connections
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = "Reset Postgresql DB"

    output_transaction = True

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help='Nominates a database to print the SQL for. Defaults to the "default" database.',
        )

    def handle(self, **options):
        base_dir = settings.BASE_DIR
        opt = settings.DATABASES[options["database"]]

        # Drop database
        if opt["ENGINE"] == "django.db.backends.postgresql":
            db_name = opt["NAME"]
            db_user = opt["USER"]
            conn_params = {"database": "template1"}
            conn_params["host"] = opt["HOST"]
            conn_params["port"] = opt["PORT"]
            conn_params["user"] = opt["USER"]
            connection = psycopg2.connect(**conn_params)
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{0}';".format(
                        db_name
                    )
                )
                cursor.execute("DROP DATABASE {0};".format(db_name))
                cursor.execute("CREATE DATABASE {0};".format(db_name))
                cursor.execute(
                    "GRANT ALL PRIVILEGES ON DATABASE {0} TO {1};".format(
                        db_name, db_user
                    )
                )

        # Delete migration files
        os.system(
            'find {0}/src -path "*/migrations/*.py" -not -name "__init__.py" -delete'.format(
                base_dir
            )
        )

        # Run migrate
        os.system("{0}/venv/bin/python manage.py makemigrations".format(base_dir))
        os.system("{0}/venv/bin/python manage.py migrate".format(base_dir))
        os.system("{0}/venv/bin/python manage.py loaddata db.json".format(base_dir))

        # Create superuser
        os.environ["DJANGO_SUPERUSER_PASSWORD"] = "admin"
        os.environ["DJANGO_SUPERUSER_USERNAME"] = "admin"
        os.environ["DJANGO_SUPERUSER_EMAIL"] = "admin@monos.mn"
        os.system(
            "{0}/venv/bin/python manage.py createsuperuser --no-input".format(base_dir)
        )
        return True
