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

import os
import time

from flask import (
    Flask, abort, request, redirect, url_for, render_template, g,
    send_from_directory)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from PIL import Image, ImageDraw, ImageFont

from configuration import (
    get_args, get_db_uri, get_templates_list,
    BASE_DIR, MEME_DIR, FONT_PATH)

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
db = SQLAlchemy(app)


# Model for representing created Memes
class Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template = db.Column(db.String(80), nullable=False)
    top_text = db.Column(db.String(80), nullable=False)
    bot_text = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<Meme %r>' % self.id


@app.before_first_request
def setup_db():
    # Create folder for memes if it doesn't exist
    if not os.path.exists(MEME_DIR):
        os.makedirs(MEME_DIR)
    # Create tables for models if they don't exist
    db.create_all()


@app.before_request
def setup_request_time():
    start_time = time.time()
    g.request_time = lambda: "%d ms" % ((time.time() - start_time) * 1000)


@app.route('/')
def index():
    return redirect(url_for("get_create_menu"))


@app.route('/recent', methods=['GET'])
def view_recent():
    memes = Meme.query.order_by(Meme.id.desc()).limit(20).all()
    return render_template('recent.html', memes=memes)


@app.route('/random', methods=['GET'])
def view_random():
    meme = Meme.query.order_by(func.random()).first()
    return redirect(url_for('view_meme', meme_id=meme.id))


@app.route('/template', methods=['GET'])
def get_create_menu():
    templates = get_templates_list()
    return render_template('view.html', templates=templates)


@app.route('/template/<string:template>', methods=['GET'])
def get_create(template):
    if template not in get_templates_list():
        abort(400, "Template does not exist.")
    return render_template('create_meme.html', template=template)


@app.route('/meme/<int:meme_id>', methods=['GET'])
def view_meme(meme_id):
    meme_file = os.path.join(MEME_DIR, '%d.png' % meme_id)
    if not os.path.exists(meme_file):
        generate_meme(meme_file, meme_id)
    print(meme_file)
    return send_from_directory(MEME_DIR, '%d.png' % meme_id)


@app.route('/meme', methods=['POST'])
def create_meme():
    try:
        meme = Meme(
            template=request.form['template'],
            top_text=request.form['top'],
            bot_text=request.form['bottom']
        )
        db.session.add(meme)
        db.session.commit()

        return redirect(url_for('view_meme', meme_id=meme.id))
    except KeyError:
        abort(400, "Incorrect parameters.")


def generate_meme(file, meme_id):
    # Query for meme
    meme = Meme.query.filter(Meme.id == meme_id).first()
    if meme is None:
        abort(400, 'Meme does not exist.')
    # Load template
    template_file = os.path.join(
        BASE_DIR, 'static', 'templates', meme.template)
    if not os.path.exists(template_file):
        abort(400, 'Template does not exist')
    template = Image.open(template_file)
    # Get Font Details
    font, top_loc, bot_loc = calc_font_details(
        meme.top_text, meme.bot_text, template.size)
    draw = ImageDraw.Draw(template)
    draw_text(draw, top_loc[0], top_loc[1], meme.top_text, font)
    draw_text(draw, bot_loc[0], bot_loc[1], meme.bot_text, font)

    template.save(file)


# Calculate font size and location
def calc_font_details(top, bot, img_size):
    font_size = 50
    font = ImageFont.truetype(FONT_PATH, font_size)
    max_width = img_size[0] - 20
    # Get ideal font size
    while font.getsize(top)[0] > max_width or font.getsize(bot)[0] > max_width:
        font_size = font_size - 1
        font = ImageFont.truetype(FONT_PATH, font_size)
    # Get font locations
    top_loc = ((img_size[0] - font.getsize(top)[0])/2, -5)
    bot_size = font.getsize(bot)
    bot_loc = ((img_size[0] - bot_size[0])/2, img_size[1] - bot_size[1] - 5)
    return font, top_loc, bot_loc


# Draws the given text with a border
def draw_text(draw, x, y, text, font):
    # Draw border
    draw.text((x-1, y-1), text, font=font, fill="black")
    draw.text((x+1, y-1), text, font=font, fill="black")
    draw.text((x-1, y+1), text, font=font, fill="black")
    draw.text((x+1, y+1), text, font=font, fill="black")
    # Draw text
    draw.text((x, y), text, font=font, fill="white")


if __name__ == '__main__':
    # Run dev server (for debugging only)
    args = get_args()
    app.run(host=args.host, port=args.port, debug=True)
