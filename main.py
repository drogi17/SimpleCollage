# NEW PROJECT
import json
import math
from math import perm

from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass
from typing import List


def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


@dataclass
class TemplateImg:
    type: str
    size: List[int]
    position: List[int]
    crop: List[list]
    rotate: int
    auto_resize: bool
    corners_radius: int


class Template:
    color: tuple
    watermark: bool
    size: List[int] = []
    objects: List[TemplateImg] = []
    images_objects: List[Image.Image] = []
    main_sheet: Image.Image
    

    def __init__(self, json_file: open = None, json_string: str = None) -> None:
        if json_file:
            self.loads(json_file.read())
        elif json_string:
            self.loads(json_string)

    def load_data(self, objects: list, size: list, color, watermark: bool) -> None:
        for object in objects:
            self.objects.append(TemplateImg(**object))
        self.size = size
        self.color = tuple(color)
        self.watermark = watermark
    

    def loads(self, json_string: str):
        json_dict = json.loads(json_string)
        if "objects" not in json_dict or "size" not in json_dict:
            return False
        self.load_data(json_dict.get("objects"), json_dict.get("size"), json_dict.get("color"), json_dict.get("watermark"))
        return self
    
    
    def add_objects(self, *objsect: List[Image.Image]):
        self.images_objects += objsect
    
    
    def create_main_sheet(self):
        if self.size:
            self.main_sheet = Image.new("RGBA", self.size, self.color)


    def add_corners_to_iamges(self):
        img_num = 0
        while img_num < len(self.objects):
            radius = self.objects[img_num].corners_radius
            self.images_objects[img_num] = add_corners(self.images_objects[img_num], radius)
            img_num += 1
    

    def resize_images(self):
        img_num = 0
        while img_num < len(self.objects):
            size = self.objects[img_num].size
            if self.objects[img_num].auto_resize:
                self.images_objects[img_num].thumbnail(size, Image.ANTIALIAS)
            else:
                self.images_objects[img_num] = self.images_objects[img_num].resize(size, Image.ANTIALIAS)
            img_num += 1
    

    def rotate_images(self):
        img_num = 0
        while img_num < len(self.objects):
            img_x, img_y = self.images_objects[img_num].size
            new_img_x = math.sin(math.pi / 180 * self.objects[img_num].rotate) * img_x
            new_img_y = math.cos(math.pi / 180 * self.objects[img_num].rotate) * img_x
            new_img_x = abs(round(new_img_x))
            new_img_y = abs(round(new_img_y))
            if new_img_x + new_img_y == 0:
                temp_img = Image.new('RGBA', [img_x, img_y])
            else:
                temp_img = Image.new('RGBA', [new_img_x + new_img_y, new_img_x + new_img_y])
            paste_x = (temp_img.width - img_x)//2
            paste_y = (temp_img.height - img_y)//2
            temp_img.paste(self.images_objects[img_num], [paste_x, paste_y])
            self.images_objects[img_num] = temp_img.rotate(self.objects[img_num].rotate)
            img_num += 1
    
    def crop_images(self):
        img_num = 0
        while img_num < len(self.objects):
            for crop in self.objects[img_num].crop:
                self.images_objects[img_num] = self.images_objects[img_num].crop(crop)
            img_num += 1
    
    def add_watermark(self):
        font = ImageFont.truetype("fonts/main.ttf", 25)
        if self.watermark:
            draw = ImageDraw.Draw(self.main_sheet)
            draw.multiline_text((10, self.main_sheet.height - 75),"Made by: SimpleCollage\n"
                                                                   "Author: @ic_it\n"
                                                                   "Project page: https://github.com/drogi17/SimpleCollage", 
                                                                   (0, 0, 0), font=font)


    def prepare_all_images(self):
        self.add_corners_to_iamges()
        self.resize_images()
        self.rotate_images()
        self.crop_images()


    def paste_imgaes(self):
        if not self.main_sheet:
            return False
        img_num = 0
        while img_num < len(self.objects):
            self.main_sheet.paste(self.images_objects[img_num], self.objects[img_num].position, self.images_objects[img_num])
            img_num += 1
    

    def save(self, name:str = "export_image.png"):
        self.main_sheet.save(name)
        
    
    def _save_temp_imgs(self):
        num = 0
        for img in self.images_objects:
            
            img.convert("RGB").save("temp/" + str(num) + ".jpg")
            num += 1


template = Template(open("templates/standart.json", "r"))
template.create_main_sheet()

image1 = Image.open("img.jpg").convert("RGBA")
image2 = Image.open("img1.jpg").convert("RGBA")
image3 = Image.open("img2.jpg").convert("RGBA")
image4 = Image.open("img3.jpg").convert("RGBA")
image5 = Image.open("img4.jpg").convert("RGBA")
image6 = Image.open("img5.jpg").convert("RGBA")

template.add_objects(image1, image2, image3, image4, image5,
                     image6, image1, image2, image3, image4, image5, image6, image1)
template.prepare_all_images()
# template._save_temp_imgs()
template.paste_imgaes()
template.add_watermark()
template.save()
