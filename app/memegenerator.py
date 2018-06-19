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

from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import os

font_path = "static/fonts/Impact.ttf"


def gen_meme(image_name, top, bottom, meme_id):
    top = top.upper()
    bottom = bottom.upper()
    image_path = os.path.join('static/images', image_name)

    img = Image.open(str(image_path))
    img_size = img.size

# find biggest font size that works
    font_size = img_size[1]/5
    # todo(sixela): fix font size calculation
    font = ImageFont.truetype(font_path, 14)
    top_text_size = font.getsize(top)
    bottom_text_size = font.getsize(bottom)
    while (top_text_size[0] > img_size[0]-20
           or bottom_text_size[0] > img_size[0] - 20):
        font_size = font_size - 1
        font = ImageFont.truetype(font_path, font_size)
        top_text_size = font.getsize(top)
        bottom_text_size = font.getsize(bottom)

    # find top centered position for top text
    top_text_x = (img_size[0]/2) - (top_text_size[0]/2)
    top_text_y = 0
    top_text_pos = (top_text_x, top_text_y)

    # find bottom centered position for bottom text
    bottom_text_y = (img_size[0]/2) - (bottom_text_size[0]/2)
    bottom_text_x = img_size[1] - bottom_text_size[1]
    bottom_text_pos = (bottom_text_y, bottom_text_x)

    draw = ImageDraw.Draw(img)

    # draw outlines
    # there may be a better way

    # todo(sixela): better handle calculation
    # outline_range = font_size/15
    outline_range = 1

    for x in range(-outline_range, outline_range+1):
        for y in range(-outline_range, outline_range+1):
            draw.text(
                (top_text_pos[0]+x, top_text_pos[1]+y),
                top, (0, 0, 0), font=font)
            draw.text(
                (bottom_text_pos[0]+x, bottom_text_pos[1]+y),
                bottom, (0, 0, 0), font=font)

    draw.text(top_text_pos, top, (255, 255, 255), font=font)
    draw.text(bottom_text_pos, bottom, (255, 255, 255), font=font)

    img.save("static/memes/%s.png" % meme_id)


if __name__ == '__main__':
    gen_meme("Hello", "World", "aliens")
