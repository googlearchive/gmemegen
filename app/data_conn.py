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

import html

# todo(sixela): implement paging instead of limits


def get_health(cursor):
    # Check if tables exists
    cursor.execute(
        "SELECT EXISTS ( SELECT 1 FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_name = 'image')")
    return cursor.fetchone()


def get_images(cursor):
    cursor.execute('select * from image order by id desc limit 20')
    return cursor.fetchall()


def get_memes(cursor):
    cursor.execute('SELECT * from meme order by id desc limit 20')
    return cursor.fetchall()


def get_recent(cursor):
    cursor.execute('SELECT * from recent order by id desc limit 20')
    return cursor.fetchall()


def create_meme(cursor, image_id, top, bottom):
    cursor.execute(
        "INSERT INTO meme (image_id, top, bottom ) "
        "VALUES (%d, '%s', '%s') RETURNING id"
        % (image_id, html.escape(top), html.escape(bottom)))
    return cursor.fetchone()[0]


def get_image_path(cursor, image_id):
    cursor.execute('SELECT name from image WHERE id=%d' % image_id)
    return cursor.fetchone()[0]


def create_image(cursor, img_name):
    cursor.execute(
        "INSERT into image (name) values ('%s') RETURNING id"
        % html.escape(img_name))
    return cursor.fetchone()[0]


def create_schema(cursor):
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS meme '
        '(id SERIAL PRIMARY KEY, image_id INTEGER, top text, bottom text);')
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS image '
        '(id SERIAL PRIMARY KEY, name text UNIQUE);')

    cursor.execute(
        "INSERT INTO image ( name ) VALUES "
        "('aliens.jpg'),('awkwardpenguin.jpg'),('successkid.jpg'),"
        "('confessionbear.jpg'),('blb.png'),('bill-lumbergh.jpg'),"
        "('homer.gif') ON CONFLICT DO NOTHING")

    return 1
