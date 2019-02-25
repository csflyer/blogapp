# @Time : 2019-02-18 17:05 
# @Author : Crazyliu
# @File : verify_code.py

# coding=utf-8
import random
from io import BytesIO
from flask import current_app
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class VerifyImage(object):
    def __init__(self, size=(20 * 4, 22), fontsize=20):
        self.size = size
        self.font = ImageFont.truetype(current_app.config['VALIDATE_CODE_FONT_PATH'], fontsize)
        self.image = Image.new('RGBA', self.size, (255, ) * 4)
        self.draw = ImageDraw.Draw(self.image)
        self.code = self.rand_text()

    @staticmethod
    def rand_text():
        source = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                  'U','V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        return ''.join(random.sample(source, 4))

    @staticmethod
    def rand_color():
        return random.randint(64, 255), random.randint(64, 255), random.randint(64, 255)

    @staticmethod
    def rand_color2():
        return random.randint(32, 127), random.randint(32, 127), random.randint(32, 127)

    def rand_point(self):
        return random.randint(0, self.size[0]), random.randint(0, self.size[1])

    def rand_line(self):
        return self.rand_point() +self.rand_point()

    def rotate(self):
        rot = self.image.rotate(random.randint(-5, 5), expand=0)
        fff = Image.new('RGBA', rot.size, (255, ) * 4)
        self.image = Image.composite(rot, fff, rot)

    def draw_text(self):
        for i, t in enumerate(list(self.code)):
            self.draw.text((18 * i, -2), t, font=self.font, fill=self.rand_color2())

    def draw_line(self):
        for i in range(random.randint(2, 5)):
            self.draw.line(self.rand_line(), fill=self.rand_color())

    def draw_transform(self):
        data = [1 - float(random.randint(1, 2)) / 100, 0, 0, 0,
                1 - float(random.randint(1, 10)) / 100,
                float(random.randint(1, 2)) / 500, 0.001,
                float(random.randint(1, 2)) / 500
                ]
        self.image = self.image.transform(self.size, Image.PERSPECTIVE, data)

    def draw_output(self):
        print(self.code)
        self.draw_text()
        self.draw_line()
        self.draw_transform()

    def save(self):
        self.draw_output()
        buff = BytesIO()
        self.image.save(buff, 'bmp')
        return buff.getvalue()

