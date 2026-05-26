from PIL import Image, ImageDraw, ImageOps
from pathlib import Path
from utils import color_change, paste_correctly, get_json, to_int, apply_mask, qr_image
from utils import text_draw_new as text_draw


BASE_DIR = str(Path(__file__).resolve().parent) + '/resources/'


class Objekt:
    def __init__(self, text_color='#000000', background_color='#FFFFFF', artist_name=None, group_name=None, number=None, alphabet='', serial=None):

        self.raw_img = None
        self.front_ready_img = Image.open(BASE_DIR+'test.png')
        self.front_img = Image.open(BASE_DIR+'test.png')


        self.back_img = Image.open(BASE_DIR+'test.png')


        self.text_color = text_color
        self.background_color = background_color
        self.artist_name = artist_name
        self.group_name = group_name

        self.number = number
        self.alphabet = alphabet
        self.serial = serial

        self.group_logo_side = None

        self.sidebar_img = color_change(Image.open(BASE_DIR+'sidebar.png'), self.background_color)
        self.sidebar = Image.new('RGBA', self.sidebar_img.size, (0,0,0,0))

        self.front = self.Front(self)
        self.back = self.Back(self)

    def set_group_logo_side(self, group_logo_side: Image.Image):
        self.group_logo_side = group_logo_side
        return self

    def draw_sidebar(self):



        draw = ImageDraw.Draw(self.sidebar)
        text_draw(self.sidebar_img.size, draw, (self.sidebar_img.size[0] * 52 / 1479, self.sidebar_img.size[1]/2), 'Helvetica_Neue_LT_Std_75_Bold.otf', 56, self.artist_name, self.text_color, align=['left', 'cap_center'])

        if self.group_logo_side:
            self.sidebar_img = paste_correctly(self.sidebar_img, to_int(self.sidebar_img.size[0]- self.sidebar_img.size[0] * 52 / 1479, (self.sidebar_img.size[1] - self.group_logo_side.size[1])/2), self.group_logo_side)
        else:
            text_draw(self.sidebar_img.size, draw, (self.sidebar_img.size[0] * 52 / 1479, self.sidebar_img.size[1]/2), 'Helvetica_Neue_LT_Std_75_Bold.otf', 56, self.group_name, self.text_color, align=['right', 'cap_center'])

        return self

    def draw_serial(self):
        draw = ImageDraw.Draw(self.sidebar_img)

        if self.number and self.serial:
            text_draw(self.sidebar.size, draw, (self.sidebar.size[0] / 2, self.sidebar.size[1]/2), 'Inter-Bold-5.ttf', 54, self.number+self.alphabet, self.text_color, align=['right', 'cap_center'])
            text_draw(self.sidebar.size, draw, (self.sidebar.size[0] / 2, self.sidebar.size[1]/2), 'MatrixSSK_custom.ttf', 60, '#'+str(self.serial).zfill(6), self.text_color, align=['left', 'cap_center'])
            print(self.sidebar_img.size[0] / 2 * (1 - 3.044/ 100))
        if self.number and not self.serial:
            text_draw(self.sidebar_img.size, draw, (self.sidebar_img.size[0] / 2, self.sidebar_img.size[1] / 2), 'Inter-Bold-5.ttf', 56, self.number+self.alphabet, self.text_color, align=['center', 'cap_center'])

        return self

    class Front:
        def __init__(self, owner):
            self.owner = owner   # A 인스턴스








        def set_raw_img(self, base: Image.Image | str):
            if isinstance(base, str):
                base = Image.open(base)

            self.owner.raw_img = base
            self.owner.front_ready_img = base
            self.owner.front_img = base
            return self

        def round_corner(self):
            self.owner.front_ready_img = apply_mask(self.owner.front_ready_img, BASE_DIR+f'blank_alpha.png')
            return self

        def resize(self):
            self.owner.front_ready_img = ImageOps.fit(self.owner.front_ready_img, (1083, 1673))
            return


        def set_sidebar_img(self, sidebar_img: Image.Image=None):
            if not sidebar_img:
                sidebar_img = Image.open(BASE_DIR+'sidebar.png')
                sidebar_img = color_change(sidebar_img, self.owner.background_color)
                sidebar_img = sidebar_img.rotate(270, expand=True)

            self.owner.front_img = paste_correctly(
                self.owner.front_img,
                to_int(self.owner.front_ready_img.size[0]-sidebar_img.size[0], (self.owner.front_ready_img.size[1]-sidebar_img.size[1])/2),
                sidebar_img
            )
            self.owner.front_img.show()
            return self




        def attach_sidebar(self):
            #self.owner.front_img = paste_correctly(self.

            self.owner.sidebar = self.owner.sidebar.rotate(270, expand=True)
            self.owner.front_img = paste_correctly(
                self.owner.front_img,
                to_int(self.owner.front_ready_img.size[0]-self.owner.sidebar.size[0], (self.owner.front_ready_img.size[1]-self.owner.sidebar.size[1])/2),
                self.owner.sidebar
            )
            return self

        def show(self):
            self.owner.front_img.show()
            return self

    class Back:
        def __init__(self, owner):
            self.owner = owner
            self.classes = None
            self.season = None

            self.back_ready_img = Image.open(BASE_DIR+'blank_alpha.png')

        def __call__(self, classes:str|None, season:str|None):
            self.classes = classes
            self.season = season
            return self

        def change_outline_color(self, color='#FFFFFF'):
            self.back_ready_img = color_change(self.back_ready_img, color)
            return self

        def attach_layout(self):
            inside = Image.open(BASE_DIR+'inside.png')
            inside = color_change(inside, self.owner.background_color)

            self.back_ready_img = paste_correctly(self.back_ready_img, to_int(0, (self.back_ready_img.size[1]-inside.size[1])/2), inside)

            layout = Image.open(BASE_DIR+'layout.png')
            layout = color_change(layout, self.owner.text_color)

            self.back_ready_img = paste_correctly(self.back_ready_img, (0, 0), layout)


            return self
        def show(self):
            self.back_ready_img.show()
            return self

        def save(self):
            self.back_ready_img.save('test.png')
            return self

        def draw_text(self):
            draw = ImageDraw.Draw(self.back_ready_img)

            if self.owner.artist_name:
                text_draw(
                    self.back_ready_img.size,
                    draw,
                    (50, 434),
                    'Helvetica_Neue_LT_Std_65_Medium-4.otf',
                    126 if len(self.owner.artist_name) < 12 else 110,
                    self.owner.artist_name,
                    self.owner.text_color,
                    align="left"
                )
            if self.classes:
                text_draw(
                    self.back_ready_img.size,
                    draw,
                    (50, 652),
                    'Helvetica_Neue_LT_Std_65_Medium-4.otf',
                    126 if len(self.classes) < 12 else 110,
                    self.classes,
                    self.owner.text_color,
                    align="left"
                )
            if self.season:
                if len(self.season.split('/')) >= 2:
                    x, *_ = text_draw(
                        self.back_ready_img.size,
                        draw,
                        (50, 874),
                        'Helvetica_Neue_LT_Std_65_Medium-4.otf',
                        126 if len(self.season) - 1 < 12 else 110,
                        self.season.split('/')[0],
                        self.owner.text_color,
                        align="left"
                    )
                    text_draw(
                        self.back_ready_img.size,
                        draw,
                        (50+x, 874),
                        'Helvetica_Neue_LT_Std_65_Medium-4-outline.otf',
                        126 if len(self.season) - 1 < 12 else 110,
                        self.season.split('/')[-1],
                        self.owner.text_color,
                        align="left"
                    )
                else:
                    text_draw(
                        self.back_ready_img.size,
                        draw,
                        (50, 874),
                        'Helvetica_Neue_LT_Std_65_Medium-4.otf',
                        126 if len(self.season) < 12 else 110,
                        self.season,
                        self.owner.text_color,
                        align="left"
                    )

            return self

        def attach_sign(self, sign: Image.Image, position:tuple[int, int]|None=None):
            sign = color_change(sign, self.owner.text_color)
            if position:
                self.back_ready_img = paste_correctly(self.back_ready_img, position, sign)
            else:
                self.back_ready_img = paste_correctly(self.back_ready_img, (74, 1065), sign)
            return self

        def attach_qr_code(self, url='https://objektify.xyz', caption='https://objektify.xyz', logo=None):
            qr_code = qr_image(url, logo)
            self.back_ready_img = paste_correctly(self.back_ready_img, (514, 1020), qr_code)

            if caption:
                draw = ImageDraw.Draw(self.back_ready_img)

                text_draw(
                    self.back_ready_img.size,
                    draw,
                    (670, 1348+12),
                    'Helvetica_Neue_LT_Std_65_Medium-4.otf',
                    32,
                    caption,
                    self.owner.text_color,
                    align="center"
                )

            return self
        def attach_top_logo(self, logo:Image.Image):
            logo = color_change(logo, self.owner.text_color)

            self.back_ready_img = paste_correctly(self.back_ready_img, (57, 151), logo)
            return self
        def draw_sidebar(self):
            

            return self
if __name__ == "__main__":
    objekt = Objekt(artist_name='JUUN', group_name='h2h', number='123', background_color='#FFFF00')
    objekt.draw_sidebar().draw_serial()
    #objekt.front.set_sidebar_img().attach_sidebar().show()
    #objekt.front.show()
    objekt.back('Pretty', 'Rude/01').attach_layout().draw_text().attach_qr_code().show().save()