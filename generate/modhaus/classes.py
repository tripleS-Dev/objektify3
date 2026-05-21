from PIL import Image, ImageDraw, ImageOps
from pathlib import Path
from utils import color_change, paste_correctly, get_json, to_int, apply_mask
from utils import text_draw_new as text_draw


BASE_DIR = str(Path(__file__).resolve().parent) + '/resources/'


class Objekt:
    def __init__(self, text_color, background_color, artist_name, group_name, number, alphabet, serial):

        self.raw_img = None
        self.front_ready_img = Image.open(BASE_DIR+'test.png')
        self.front_img = Image.open(BASE_DIR+'test.png')


        self.text_color = text_color
        self.background_color = background_color
        self.artist_name = artist_name
        self.group_name = group_name

        self.number = number
        self.alphabet = alphabet
        self.serial = serial

        self.group_logo_side = None

        sidebar = Image.open(BASE_DIR+'sidebar.png')
        self.sidebar_img = color_change(sidebar, self.background_color)

    def set_raw_img(self, base: Image.Image | str):
        if isinstance(base, str):
            base = Image.open(base)

        self.raw_img = base
        self.front_ready_img = base
        self.front_img = base
        return self

    def round_corner(self):
        self.front_ready_img = apply_mask(self.front_ready_img, BASE_DIR+f'blank_alpha.png')
        return self

    def resize(self):
        self.front_ready_img = ImageOps.fit(self.front_ready_img, (1083, 1673))
        return

    def set_group_logo_side(self, group_logo_side: Image.Image):
        self.group_logo_side = group_logo_side
        return self

    def set_sidebar_img(self, sidebar_img: Image.Image):
        self.sidebar_img = sidebar_img
        return self

    def draw_sidebar(self):



        draw = ImageDraw.Draw(self.sidebar_img)
        text_draw(self.sidebar_img.size, draw, (self.sidebar_img.size[0] * 52 / 1479, self.sidebar_img.size[1]/2), 'Helvetica_Neue_LT_Std_75_Bold.otf', 56, self.artist_name, self.text_color, align=['left', 'cap_center'])

        if self.group_logo_side:
            self.sidebar_img = paste_correctly(self.sidebar_img, to_int(self.sidebar_img.size[0]- self.sidebar_img.size[0] * 52 / 1479, (self.sidebar_img.size[1] - self.group_logo_side.size[1])/2), self.group_logo_side)
        else:
            text_draw(self.sidebar_img.size, draw, (self.sidebar_img.size[0] * 52 / 1479, self.sidebar_img.size[1]/2), 'Helvetica_Neue_LT_Std_75_Bold.otf', 56, self.group_name, self.text_color, align=['right', 'cap_center'])


        return self

    def draw_serial(self):
        draw = ImageDraw.Draw(self.sidebar_img)

        if self.number and self.serial:
            text_draw(self.sidebar_img.size, draw, (self.sidebar_img.size[0] / 2, self.sidebar_img.size[1]/2), 'Inter-Bold-5.ttf', 54, self.number+self.alphabet, self.text_color, align=['right', 'cap_center'])
            text_draw(self.sidebar_img.size, draw, (self.sidebar_img.size[0] / 2, self.sidebar_img.size[1]/2), 'MatrixSSK_custom.ttf', 60, '#'+str(self.serial).zfill(6), self.text_color, align=['left', 'cap_center'])
            print(self.sidebar_img.size[0] / 2 * (1 - 3.044/ 100))
        if self.number and not self.serial:
            text_draw(self.sidebar_img.size, draw, (self.sidebar_img.size[0] / 2, self.sidebar_img.size[1] / 2), 'Inter-Bold-5.ttf', 56, self.number+self.alphabet, self.text_color, align=['center', 'cap_center'])

        return self

    def attach_sidebar(self):
        self.sidebar_img = self.sidebar_img.rotate(270, expand=True)
        self.front_img = paste_correctly(
            self.front_ready_img,
            to_int(self.front_ready_img.size[0]-self.sidebar_img.size[0], (self.front_ready_img.size[1]-self.sidebar_img.size[1])/2),
            self.sidebar_img
        )
        return self

    def show(self):
        self.front_img.show()
        return self

if __name__ == "__main__":

    pass