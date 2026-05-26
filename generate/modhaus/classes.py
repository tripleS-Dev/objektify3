from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from PIL import Image, ImageDraw, ImageOps

from utils import (
    color_change,
    paste_correctly,
    to_int,
    apply_mask,
    qr_image,
)
from utils import text_draw_new as text_draw


BASE_DIR = Path(__file__).resolve().parent / "resources"

ImageLike = Union[Image.Image, str, Path]
Position = tuple[int, int]


@dataclass(slots=True)
class ObjektTheme:
    text_color: str = "#000000"
    background_color: str = "#FFFFFF"


@dataclass(slots=True)
class ObjektMeta:
    artist_name: Optional[str] = None
    group_name: Optional[str] = None
    number: Optional[str] = None
    alphabet: str = ""
    serial: Optional[int|str] = None

    @property
    def number_text(self) -> str:
        return f"{self.number or ''}{self.alphabet or ''}"

    @property
    def serial_text(self) -> Optional[str]:
        if self.serial is None:
            return None
        return f"#{str(self.serial).zfill(6)}"


class Assets:
    def __init__(self, base_dir: Path = BASE_DIR):
        self.base_dir = Path(base_dir)

    def path(self, filename: str) -> str:
        return str(self.base_dir / filename)

    def image(self, filename: str) -> Image.Image:
        with Image.open(self.base_dir / filename) as img:
            return img.convert("RGBA").copy()

    def font(self, filename: str) -> str:
        return filename


class Objekt:
    def __init__(
        self,
        text_color: str = "#000000",
        background_color: str = "#FFFFFF",
        artist_name: Optional[str] = None,
        group_name: Optional[str] = None,
        number: Optional[str] = None,
        alphabet: str = "",
        serial: Optional[int|str] = None,
        assets: Optional[Assets] = None,
    ):
        self.theme = ObjektTheme(
            text_color=text_color,
            background_color=background_color,
        )
        self.meta = ObjektMeta(
            artist_name=artist_name,
            group_name=group_name,
            number=number,
            alphabet=alphabet,
            serial=serial,
        )
        self.assets = assets or Assets()

        self.raw_img: Optional[Image.Image] = None

        self.front_ready_img = self.assets.image("test.png")
        self.front_img = self.front_ready_img.copy()

        self.group_logo_side: Optional[Image.Image] = None

        # 앞면용 sidebar 캐시
        self.sidebar_img = self.make_sidebar_text_layer(
            use_background=True,
            include_serial=False,
        )

        self.front = FrontRenderer(self)
        self.back = BackRenderer(self)

    # ------------------------------------------------------------------
    # 편의 property
    # ------------------------------------------------------------------
    @property
    def text_color(self) -> str:
        return self.theme.text_color

    @property
    def background_color(self) -> str:
        return self.theme.background_color

    @property
    def artist_name(self) -> Optional[str]:
        return self.meta.artist_name

    @property
    def group_name(self) -> Optional[str]:
        return self.meta.group_name

    # ------------------------------------------------------------------
    # 공통 sidebar 관련
    # ------------------------------------------------------------------
    def set_group_logo_side(self, group_logo_side: Image.Image) -> Objekt:
        self.group_logo_side = group_logo_side.convert("RGBA").copy()
        return self

    def make_sidebar_text_layer(
        self,
        use_background: bool = False,
        include_serial: bool = True,
    ) -> Image.Image:
        """
        Sidebar 텍스트 레이어 생성.

        - use_background=True:
            sidebar.png를 배경색으로 칠한 뒤 그 위에 텍스트를 그림
            => 앞면용

        - use_background=False:
            sidebar.png와 같은 크기의 완전 투명한 캔버스에 텍스트만 그림
            => 뒷면용
        """
        sidebar_base = self.assets.image("sidebar.png")

        if use_background:
            sidebar = color_change(sidebar_base, self.theme.background_color)
        else:
            sidebar = Image.new("RGBA", sidebar_base.size, (0, 0, 0, 0))

        draw = ImageDraw.Draw(sidebar)
        width, height = sidebar.size
        margin_x = width * 52 / 1479

        # 왼쪽: artist_name
        if self.meta.artist_name:
            text_draw(
                sidebar.size,
                draw,
                (margin_x, height / 2),
                self.assets.font("Helvetica_Neue_LT_Std_75_Bold.otf"),
                56,
                self.meta.artist_name,
                self.theme.text_color,
                align=["left", "cap_center"],
            )

        # 오른쪽: group_logo_side 또는 group_name
        if self.group_logo_side:
            x = width - margin_x - self.group_logo_side.size[0]
            y = (height - self.group_logo_side.size[1]) / 2
            sidebar = paste_correctly(
                sidebar,
                to_int(x, y),
                self.group_logo_side,
            )
        elif self.meta.group_name:
            text_draw(
                sidebar.size,
                draw,
                (margin_x, height / 2),
                self.assets.font("Helvetica_Neue_LT_Std_75_Bold.otf"),
                56,
                self.meta.group_name,
                self.theme.text_color,
                align=["right", "cap_center"],
            )

        if include_serial:
            center = (width / 2, height / 2)

            if self.meta.number and self.meta.serial_text:
                text_draw(
                    sidebar.size,
                    draw,
                    center,
                    self.assets.font("Inter-Bold-5.ttf"),
                    54,
                    self.meta.number_text,
                    self.theme.text_color,
                    align=["right", "cap_center"],
                )
                text_draw(
                    sidebar.size,
                    draw,
                    center,
                    self.assets.font("MatrixSSK_custom.ttf"),
                    60,
                    self.meta.serial_text,
                    self.theme.text_color,
                    align=["left", "cap_center"],
                )
            elif self.meta.number:
                text_draw(
                    sidebar.size,
                    draw,
                    center,
                    self.assets.font("Inter-Bold-5.ttf"),
                    56,
                    self.meta.number_text,
                    self.theme.text_color,
                    align=["center", "cap_center"],
                )

        return sidebar

    def draw_sidebar(self) -> Objekt:
        """
        앞면용 sidebar 이미지 생성
        (배경 있음, serial 없음)
        """
        self.sidebar_img = self.make_sidebar_text_layer(
            use_background=True,
            include_serial=False,
        )
        return self

    def draw_serial(self) -> Objekt:
        """
        앞면용 sidebar 이미지에 serial/number까지 포함하도록 다시 생성
        """
        self.sidebar_img = self.make_sidebar_text_layer(
            use_background=True,
            include_serial=True,
        )
        return self


class FrontRenderer:
    def __init__(self, owner: Objekt):
        self.owner = owner
        self._sidebar_override: Optional[Image.Image] = None

    def set_raw_img(self, base: ImageLike) -> FrontRenderer:
        image = self._load_image(base)
        self.owner.raw_img = image.copy()
        self.owner.front_ready_img = image.copy()
        self.owner.front_img = image.copy()
        return self

    def resize(self, size: tuple[int, int] = (1083, 1673)) -> FrontRenderer:
        self.owner.front_ready_img = ImageOps.fit(self.owner.front_ready_img, size)
        self.owner.front_img = self.owner.front_ready_img.copy()
        return self

    def round_corner(self, mask_filename: str = "blank_alpha.png") -> FrontRenderer:
        self.owner.front_ready_img = apply_mask(
            self.owner.front_ready_img,
            self.owner.assets.path(mask_filename),
        )
        self.owner.front_img = self.owner.front_ready_img.copy()
        return self

    def set_sidebar_img(self, sidebar_img: Optional[Image.Image] = None) -> FrontRenderer:
        """
        앞면에 붙일 sidebar 이미지를 설정만 함.
        실제 합성은 attach_sidebar()에서 수행.
        """
        if sidebar_img is None:
            sidebar_img = self.owner.sidebar_img
        self._sidebar_override = sidebar_img.convert("RGBA").copy()
        return self

    def attach_sidebar(self, sidebar_img: Optional[Image.Image] = None) -> FrontRenderer:
        sidebar = sidebar_img or self._sidebar_override or self.owner.sidebar_img
        sidebar = sidebar.convert("RGBA").rotate(270, expand=True)

        # 중요:
        # 매번 무거운 resize / round_corner를 다시 하지 않고,
        # 이미 처리된 front_ready_img에서 새 final 이미지를 생성
        base = self.owner.front_ready_img.copy()

        self.owner.front_img = paste_correctly(
            base,
            to_int(
                base.size[0] - sidebar.size[0],
                (base.size[1] - sidebar.size[1]) / 2,
            ),
            sidebar,
        )
        return self

    def image(self) -> Image.Image:
        return self.owner.front_img.copy()

    def show(self) -> FrontRenderer:
        self.owner.front_img.show()
        return self

    def save(self, path: Union[str, Path]) -> FrontRenderer:
        self.owner.front_img.save(path)
        return self

    @staticmethod
    def _load_image(base: ImageLike) -> Image.Image:
        if isinstance(base, Image.Image):
            return base.convert("RGBA").copy()
        with Image.open(base) as img:
            return img.convert("RGBA").copy()


class BackRenderer:
    def __init__(self, owner: Objekt):
        self.owner = owner
        self.classes: Optional[str] = None
        self.season: Optional[str] = None
        self.back_ready_img = self.owner.assets.image("blank_alpha.png")

    def __call__(
        self,
        classes: Optional[str] = None,
        season: Optional[str] = None,
    ) -> BackRenderer:
        self.classes = classes
        self.season = season
        return self

    def reset(self) -> BackRenderer:
        self.back_ready_img = self.owner.assets.image("blank_alpha.png")
        return self

    def change_outline_color(self, color: str = "#FFFFFF") -> BackRenderer:
        self.back_ready_img = color_change(self.back_ready_img, color)
        return self

    def attach_layout(self) -> BackRenderer:
        inside = self.owner.assets.image("inside.png")
        inside = color_change(inside, self.owner.theme.background_color)

        self.back_ready_img = paste_correctly(
            self.back_ready_img,
            to_int(0, (self.back_ready_img.size[1] - inside.size[1]) / 2),
            inside,
        )

        layout = self.owner.assets.image("layout.png")
        layout = color_change(layout, self.owner.theme.text_color)

        self.back_ready_img = paste_correctly(
            self.back_ready_img,
            (0, 0),
            layout,
        )
        return self

    def draw_text(self) -> BackRenderer:
        draw = ImageDraw.Draw(self.back_ready_img)

        self._draw_main_text(draw, self.owner.meta.artist_name, (50, 434))
        self._draw_main_text(draw, self.classes, (50, 652))
        self._draw_season(draw)

        return self

    def draw_sidebar(self) -> BackRenderer:
        """
        뒷면용 sidebar:
        앞면과 같은 배치지만 sidebar 배경 이미지는 사용하지 않고,
        완전 투명한 레이어(0,0,0,0)에 텍스트만 그린 뒤 붙여넣음.
        """
        sidebar = self.owner.make_sidebar_text_layer(
            use_background=False,
            include_serial=True,
        )
        sidebar = sidebar.rotate(270, expand=True)

        self.back_ready_img = paste_correctly(
            self.back_ready_img,
            to_int(
                self.back_ready_img.size[0] - sidebar.size[0] - 100,
                (self.back_ready_img.size[1] - sidebar.size[1]) / 2,
            ),
            sidebar,
        )
        return self

    def attach_sign(
        self,
        sign: Image.Image,
        position: Optional[Position] = None,
    ) -> BackRenderer:
        sign = color_change(sign.convert("RGBA"), self.owner.theme.text_color)

        self.back_ready_img = paste_correctly(
            self.back_ready_img,
            position or (74, 1065),
            sign,
        )
        return self

    def attach_qr_code(
        self,
        url: str = "https://objektify.xyz",
        caption: Optional[str] = "https://objektify.xyz",
        logo: Optional[Image.Image] = None,
    ) -> BackRenderer:
        qr_code = qr_image(url, logo)
        self.back_ready_img = paste_correctly(
            self.back_ready_img,
            (514, 1020),
            qr_code,
        )

        if caption:
            draw = ImageDraw.Draw(self.back_ready_img)
            text_draw(
                self.back_ready_img.size,
                draw,
                (670, 1360),
                self.owner.assets.font("Helvetica_Neue_LT_Std_65_Medium-4.otf"),
                32,
                caption,
                self.owner.theme.text_color,
                align="center",
            )

        return self

    def attach_top_logo(self, logo: Image.Image) -> BackRenderer:
        logo = color_change(logo.convert("RGBA"), self.owner.theme.text_color)
        self.back_ready_img = paste_correctly(self.back_ready_img, (57, 151), logo)
        return self

    def image(self) -> Image.Image:
        return self.back_ready_img.copy()

    def show(self) -> BackRenderer:
        self.back_ready_img.show()
        return self

    def save(self, path: Union[str, Path]) -> BackRenderer:
        self.back_ready_img.save(path)
        return self

    def _draw_main_text(
        self,
        draw: ImageDraw.ImageDraw,
        value: Optional[str],
        position: Position,
    ) -> None:
        if not value:
            return

        font_size = 126 if len(value) < 12 else 110
        text_draw(
            self.back_ready_img.size,
            draw,
            position,
            self.owner.assets.font("Helvetica_Neue_LT_Std_65_Medium-4.otf"),
            font_size,
            value,
            self.owner.theme.text_color,
            align="left",
        )

    def _draw_season(self, draw: ImageDraw.ImageDraw) -> None:
        if not self.season:
            return

        font_regular = self.owner.assets.font("Helvetica_Neue_LT_Std_65_Medium-4.otf")
        font_outline = self.owner.assets.font("Helvetica_Neue_LT_Std_65_Medium-4-outline.otf")

        if "/" not in self.season:
            self._draw_main_text(draw, self.season, (50, 874))
            return

        left, right = self.season.split("/", 1)
        font_size = 126 if len(self.season) - 1 < 12 else 110

        x, *_ = text_draw(
            self.back_ready_img.size,
            draw,
            (50, 874),
            font_regular,
            font_size,
            left,
            self.owner.theme.text_color,
            align="left",
        )
        text_draw(
            self.back_ready_img.size,
            draw,
            (50 + x, 874),
            font_outline,
            font_size,
            right,
            self.owner.theme.text_color,
            align="left",
        )


if __name__ == "__main__":
    objekt = Objekt(
        artist_name="JUUN",
        group_name="h2h",
        number="123",
        alphabet="A",
        serial=45,
        background_color="#FFFF00",
        text_color="#000000",
    )

    # -----------------------------
    # Front example
    # -----------------------------
    objekt.draw_sidebar().draw_serial()

    objekt.front \
        .set_raw_img(BASE_DIR / "test.png") \
        .resize() \
        .round_corner() \
        .set_sidebar_img() \
        .attach_sidebar() \
        .show()

    # -----------------------------
    # Back example
    # -----------------------------
    objekt.back("Pretty", "Rude/01") \
        .reset() \
        .attach_layout() \
        .draw_text() \
        .draw_sidebar() \
        .attach_qr_code(
            url="https://objektify.xyz",
            caption="https://objektify.xyz",
        ) \
        .show()