# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEME_DIR = os.path.join(BASE_DIR, 'static', 'memes')
FONT_PATH = os.path.join(BASE_DIR, 'static', 'fonts', 'Impact.ttf')


def get_args():
    args = getattr(get_args, '_args', None)
    if args is None:
        parser = argparse.ArgumentParser()

        # Only used when running the flask debugging server
        parser.add_argument(
            '-H', '--host', default='127.0.0.1',
            help='Address for the debug webserver to listen on.')
        parser.add_argument(
            '-P', '--port', default='8080', type=int,
            help='Port for webserver to listen on.')

        parser.add_argument(
            '-d', '--db-host',
            default=os.environ.get('DB_HOST', '127.0.0.1'),
            help='Host address of the database.')
        parser.add_argument(
            '-n', '--db-name',
            default=os.environ.get('DB_NAME', 'memegen'),
            help='Name of the database.')
        parser.add_argument(
            '-u', '--db-user',
            default=os.environ.get('DB_USER', 'postgres'),
            help='User used to connect to the database.')
        parser.add_argument(
            '-p', '--db-pass',
            default=os.environ.get('DB_PASS', 'password'),
            help='Password used to connect to the database.')

        args = get_args._args = parser.parse_args()
    return args


def get_db_uri():
    args = get_args()
    return 'postgresql+pg8000://{}:{}@{}/{}'.format(
        args.db_user, args.db_pass, args.db_host, args.db_name)


def get_templates_list():
    templates = getattr(get_templates_list, '_templates', None)
    if templates is None:
        template_directory = os.path.join(BASE_DIR, 'static', 'templates')
        templates = os.listdir(template_directory)
        get_templates_list._templates = templates
    return templates
