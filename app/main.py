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
import pg8000
from flask import (
    Flask, request, g, redirect, url_for,  render_template, jsonify)
import app.memegenerator as memegenerator
import app.data_conn as data_conn

DATABASE = 'memegen.db'

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def index():
    get_health()
    return redirect(url_for("get_images"))


def get_cursor():
    cursor = getattr(g, '_database', None)

    if cursor is None:
        args = get_args()
        conn = pg8000.connect(
            user=args.db_user, password=args.db_pass, host=args.db_host)
        conn.autocommit = True
        cursor = g._database = conn.cursor()
        # Verify the schema is created
        data_conn.create_schema(cursor)

    return cursor


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/health', methods=['GET'])
def get_health():
    for i in range(3):
        try:
            result = data_conn.get_health(get_cursor())
            if result[0]:
                return jsonify({
                    'health': 'OK',
                    'message': 'Attempt {} of 3.'.format(i)
                })
            print("Result failed: {}".format(result))
        except Exception as e:
            print("Exception during health check encountered: {}".format(e))

    return jsonify({'health': 'FAIL'})


@app.route('/recent', methods=['GET'])
def get_recent():

    # todo(sixela): create table for recent and populate it
    # everytime a meme is created
    db_images = data_conn.get_recent(get_cursor())
    images = list()
    for image in db_images:
        html_image = dict()
        html_image['id_url'] = url_for('get_image', image_id=image[0])
        html_image['img_url'] = url_for('')

        images.append(html_image)

    return render_template('recent.html')


@app.route('/image', methods=['GET'])
def get_images():
    db_images = data_conn.get_images(get_cursor())
    form_data = dict()
    images = list()
    for image in db_images:
        html_image = dict()
        html_image['id_url'] = url_for('get_image', image_id=image[0])
        html_image['img_url'] = url_for('static',
                                        filename='images/%s' % image[1])
        images.append(html_image)
    form_data['images'] = images
    form_data['to_upload'] = True
    return render_template('grid.html', form_data=form_data)


@app.route('/image/<int:image_id>', methods=['GET'])
def get_image(image_id):
    image = dict()
    image['id'] = image_id
    image['name'] = data_conn.get_image_path(get_cursor(), image_id)
    return render_template('make_meme.html', image=image)


@app.route('/image', methods=['POST'])
def post_images():
    img = request.files['image']
    img.save('static/images/%s' % img.filename)
    img_id = data_conn.create_image(get_cursor(), img.filename)
    return redirect(url_for("get_image", image_id=img_id))


@app.route('/meme/<int:meme_id>', methods=['GET'])
def get_meme(meme_id):
    return redirect(url_for('static', filename='memes/%d.png' % meme_id))


@app.route('/meme', methods=['GET'])
def get_memes():
    db_images = data_conn.get_memes(get_cursor())
    form_data = dict()
    images = list()
    for image in db_images:
        html_image = dict()
        html_image['img_url'] = url_for('static',
                                        filename='memes/%d.png' % image[0])
        html_image['id_url'] = html_image['img_url']
        images.append(html_image)

    form_data['images'] = images
    form_data['to_upload'] = False
    return render_template('grid.html', form_data=form_data)


@app.route('/meme', methods=['POST'])
def post_meme():
    meme_id = data_conn.create_meme(
        get_cursor(), int(request.form['image']),
        request.form['top'], request.form['bottom'])
    image_name = data_conn.get_image_path(
        get_cursor(), int(request.form['image']))
    memegenerator.gen_meme(
        image_name, request.form['top'], request.form['bottom'], meme_id)
    return redirect(url_for('static', filename='memes/%d.png' % meme_id))


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
            '-u', '--db-user',
            default=os.environ.get('DB_USER', 'postgres'),
            help='User used to connect to the database.')
        parser.add_argument(
            '-p', '--db-pass',
            default=os.environ.get('DB_PASS', 'password'),
            help='Password used to connect to the database.')

        args = get_args._args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = get_args()

    app.debug = True
    app.run(host=args.host, port=args.port)
