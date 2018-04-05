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

import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import os

font_path = "static/fonts/Impact.ttf"
def gen_meme(image_name, top, bottom, meme_id):
    top = top.upper()
    bottom = bottom.upper()
    image_path = os.path.join('static/images',image_name)

    img = Image.open(str(image_path))
    imageSize = img.size

# find biggest font size that works
    fontSize = imageSize[1]/5
    # todo(sixela): fix font size calculation
    font = ImageFont.truetype(font_path, 14)
    topTextSize = font.getsize(top)
    bottomTextSize = font.getsize(bottom)
    while topTextSize[0] > imageSize[0]-20 or bottomTextSize[0] > imageSize[0]-20:
        fontSize = fontSize - 1
        font = ImageFont.truetype(font_path, fontSize)
        topTextSize = font.getsize(top)
        bottomTextSize = font.getsize(bottom)

# find top centered position for top text
    topTextPositionX = (imageSize[0]/2) - (topTextSize[0]/2)
    topTextPositionY = 0
    topTextPosition = (topTextPositionX, topTextPositionY)

# find bottom centered position for bottom text
    bottomTextPositionX = (imageSize[0]/2) - (bottomTextSize[0]/2)
    bottomTextPositionY = imageSize[1] - bottomTextSize[1]
    bottomTextPosition = (bottomTextPositionX, bottomTextPositionY)

    draw = ImageDraw.Draw(img)

# draw outlines
# there may be a better way
    
    # todo(sixela): better handle calculation
    # outlineRange = fontSize/15
    outlineRange = 1

    for x in range(-outlineRange, outlineRange+1):
        for y in range(-outlineRange, outlineRange+1):
            draw.text((topTextPosition[0]+x, topTextPosition[1]+y), top, (0,0,0), font=font)
            draw.text((bottomTextPosition[0]+x, bottomTextPosition[1]+y), bottom, (0,0,0), font=font)

    draw.text(topTextPosition, top, (255,255,255), font=font)
    draw.text(bottomTextPosition, bottom, (255,255,255), font=font)

    img.save("static/memes/%s.png" % meme_id)

if __name__ == '__main__':
    gen_meme("Hello", "World", "aliens")
