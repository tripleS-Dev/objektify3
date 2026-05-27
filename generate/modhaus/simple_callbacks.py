from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import gradio as gr
from PIL import Image, ImageOps, PngImagePlugin

from config import ARTIST_DIR
from generate.modhaus.classes import Objekt, ObjektMeta, ObjektTheme
from utils import (
    get_json,
    get_kr_time,
    paste_correctly,
    save_log_json,
)


DEFAULT_QR_CODE = "https://objektify.xyz/"
DEFAULT_QR_CAPTION = "https://objektify.xyz"
CACHE_DIR = Path("./cache")


@dataclass(slots=True)
class GalleryImage:
    image: Image.Image
    source_path: Optional[Path] = None


@dataclass(slots=True)
class ResolvedArtistConfig:
    artist: str
    config: dict[str, Any]
    group_name: str
    background_color: str
    text_color: str
    appearance_background: str
    season_display: Optional[str]
    default_image: Optional[Image.Image] = None
    side_logo_img: Optional[Image.Image] = None
    top_logo_img: Optional[Image.Image] = None
    qr_logo_img: Optional[Image.Image] = None
    sign_img: Optional[Image.Image] = None
    sign_position: Optional[tuple[int, int]] = None
    front_sidebar_img: Optional[Image.Image] = None
    back_inside_img: Optional[Image.Image] = None


def open_gallery_image(gallery_value: Any) -> Optional[GalleryImage]:
    items = _gallery_items(gallery_value)
    if not items:
        return None

    if len(items) >= 4 and "objektify-combined" in str(items[2]):
        if len(items) >= 5:
            gr.Info("You can only upload one image.", duration=5)
        selected = items[3]
    elif len(items) >= 2:
        gr.Info("You can only upload one image.", duration=5)
        selected = items[0]
    else:
        selected = items[0]

    source_path = Path(selected) if selected else None
    if source_path is None:
        return None

    with Image.open(source_path) as img:
        try:
            image = ImageOps.exif_transpose(img)
        except ZeroDivisionError:
            image = img.rotate(270, expand=True)
        return GalleryImage(image.convert("RGBA").copy(), source_path)


def resolve_artist_config(
    artist: str,
    member: Optional[str],
    season: Optional[str],
    class_: Optional[str],
    background_color: Optional[str],
    text_color: Optional[str],
) -> ResolvedArtistConfig:
    config_path = ARTIST_DIR / artist / "config.json"
    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    default_color = config.get("default_color") or ["#FFFFFF", "#000000"]
    default_background = default_color[0] if len(default_color) > 0 else "#FFFFFF"
    default_text = default_color[1] if len(default_color) > 1 else "#000000"

    color_spec = get_json(config, f"seasons.{season}.{class_}", None)
    background = default_background
    text = default_text
    appearance_background = background
    asset_key = None

    if isinstance(color_spec, (list, tuple)) and color_spec:
        background_token = str(color_spec[0])
        configured_text = str(color_spec[1]) if len(color_spec) > 1 else default_text

        if background_token.startswith("#"):
            background = background_token
            text = configured_text
            appearance_background = background_token
        elif background_token.startswith("@"):
            if background_token[1:] == "choose":
                background = background_color or default_background
                text = text_color or configured_text
                appearance_background = background
            else:
                text = configured_text
                appearance_background = background_token
        else:
            asset_key = background_token
            text = configured_text
            appearance_background = background_token

    default_image = _load_artist_image(artist, "default.png") if config.get("default") else None
    side_logo_img = _load_artist_image(artist, "side_logo.png") if config.get("side_logo") else None
    top_logo_img = _load_artist_image(artist, "top_logo.png") if config.get("top_logo") else None
    qr_logo_img = _load_artist_image(artist, "qr_logo.png") if config.get("qr_logo") else None

    sign_img = None
    sign_position = None
    if member and get_json(config, f"members.{member}.sign", False, bool):
        sign_img = _load_artist_image(artist, "signs", f"{member}.png")
        sign_position = get_json(config, f"members.{member}.position", None, tuple)
        if sign_img is not None and sign_position is None:
            x = int((453 - sign_img.size[0]) / 2 + 59)
            y = int((311 - sign_img.size[1]) / 2 + 1020)
            sign_position = (x, y)

    front_sidebar_img = None
    back_inside_img = None
    if asset_key:
        front_sidebar_img = _load_artist_image(artist, asset_key, "front.png")
        back_inside_img = _load_artist_image(artist, asset_key, "back.png")

    return ResolvedArtistConfig(
        artist=artist,
        config=config,
        group_name=config.get("name", artist),
        background_color=background,
        text_color=text,
        appearance_background=appearance_background,
        season_display=get_json(config, f"seasons.{season}.display", season, str),
        default_image=default_image,
        side_logo_img=side_logo_img,
        top_logo_img=top_logo_img,
        qr_logo_img=qr_logo_img,
        sign_img=sign_img,
        sign_position=sign_position,
        front_sidebar_img=front_sidebar_img,
        back_inside_img=back_inside_img,
    )


def update_simple_objekt(
    objekt: Optional[Objekt],
    temp_id: Optional[str],
    cache_id: Optional[str],
    gallery_value: Any,
    artist: Optional[str],
    season: Optional[str],
    class_: Optional[str],
    background_color: Optional[str],
    text_color: Optional[str],
    member: Optional[str],
    unit: Any,
    numbering_state: Optional[bool],
    number: Optional[str],
    alphabet: Optional[str],
    serial: Optional[str],
    qr_code: Optional[str],
) -> list[Any]:
    return _update_simple_objekt(
        objekt,
        temp_id,
        cache_id,
        gallery_value,
        artist,
        season,
        class_,
        background_color,
        text_color,
        member,
        unit,
        numbering_state,
        number,
        alphabet,
        serial,
        qr_code,
        force_gallery=False,
    )


def upload_simple_objekt(
    objekt: Optional[Objekt],
    temp_id: Optional[str],
    cache_id: Optional[str],
    gallery_value: Any,
    artist: Optional[str],
    season: Optional[str],
    class_: Optional[str],
    background_color: Optional[str],
    text_color: Optional[str],
    member: Optional[str],
    unit: Any,
    numbering_state: Optional[bool],
    number: Optional[str],
    alphabet: Optional[str],
    serial: Optional[str],
    qr_code: Optional[str],
) -> list[Any]:
    return _update_simple_objekt(
        objekt,
        temp_id,
        cache_id,
        gallery_value,
        artist,
        season,
        class_,
        background_color,
        text_color,
        member,
        unit,
        numbering_state,
        number,
        alphabet,
        serial,
        qr_code,
        force_gallery=True,
    )


def sync_simple_to_simple_plus(objekt: Optional[Objekt]) -> list[Any]:
    if not isinstance(objekt, Objekt):
        return [gr.update() for _ in range(28)]

    snapshot = getattr(objekt, "_simple_plus_snapshot", None)
    if not snapshot:
        return [gr.update() for _ in range(28)]

    mode = snapshot.get("color_mode") or "Static"
    return [
        snapshot.get("artist"),
        snapshot.get("season"),
        snapshot.get("class"),
        mode,
        gr.ColorPicker(
            value=snapshot.get("background_color") or "#FFFFFF",
            visible=mode == "Static",
        ),
        gr.Group(visible=mode == "Image"),
        snapshot.get("raw_sidebar"),
        snapshot.get("raw_back"),
        gr.Group(visible=mode == "AI Colorful"),
        None,
        None,
        None,
        snapshot.get("text_color") or "#000000",
        snapshot.get("outline_color") or "#FFFFFF",
        snapshot.get("member"),
        snapshot.get("top_logo"),
        snapshot.get("side_logo"),
        snapshot.get("sign"),
        snapshot.get("sign_x"),
        snapshot.get("sign_y"),
        snapshot.get("sign_scale") or 1,
        gr.Accordion(open=bool(snapshot.get("number") or snapshot.get("serial")), visible=True),
        snapshot.get("number") or "",
        snapshot.get("alphabet") or "",
        snapshot.get("serial") or "",
        gr.Accordion(open=bool(snapshot.get("qr_code") or snapshot.get("qr_logo")), visible=True),
        snapshot.get("qr_code") or "",
        snapshot.get("qr_logo"),
    ]


def simple_plus_color_mode_input(mode: Optional[str]) -> tuple[Any, Any, Any]:
    mode = mode or "Static"
    return (
        gr.Group(visible=mode == "Image"),
        gr.Group(visible=mode == "AI Colorful"),
        gr.ColorPicker(visible=mode == "Static"),
    )


def update_simple_plus_objekt(
    objekt: Optional[Objekt],
    temp_id: Optional[str],
    cache_id: Optional[str],
    gallery_value: Any,
    artist: Optional[str],
    season: Optional[str],
    class_: Optional[str],
    color_mode: Optional[str],
    background_color: Optional[str],
    text_color: Optional[str],
    outline_color: Optional[str],
    member: Optional[str],
    number: Optional[str],
    alphabet: Optional[str],
    serial: Optional[str],
    qr_code: Optional[str],
    top_logo: Any,
    side_logo: Any,
    sign: Any,
    sign_x: Any,
    sign_y: Any,
    sign_scale: Any,
    qr_logo: Any,
    raw_sidebar: Any,
    raw_back: Any,
    ai_sidebar: Any,
    ai_back: Any,
) -> list[Any]:
    temp_id = temp_id or get_kr_time()
    color_mode = color_mode or "Static"
    background_color = background_color or "#FFFFFF"
    text_color = text_color or "#000000"
    outline_color = outline_color or "#FFFFFF"

    if not isinstance(objekt, Objekt):
        objekt = Objekt(
            text_color=text_color,
            background_color=background_color,
            artist_name=member or "",
            group_name=artist or "",
            number=number or "",
            alphabet=alphabet or "",
            serial=serial or None,
        )

    sidebar_img = None
    back_img = None
    appearance_background = background_color
    if color_mode == "Image":
        sidebar_img = _coerce_image(raw_sidebar)
        back_img = _coerce_image(raw_back)
        appearance_background = "image"
    elif color_mode == "AI Colorful":
        sidebar_img = _coerce_image(ai_sidebar)
        back_img = _coerce_image(ai_back)
        appearance_background = "ai"

    top_logo_img = _coerce_image(top_logo)
    side_logo_img = _coerce_image(side_logo)
    sign_img = _coerce_image(sign)
    qr_logo_img = _coerce_image(qr_logo)

    qr_url = DEFAULT_QR_CODE if qr_code is None else str(qr_code).strip()
    qr_caption = DEFAULT_QR_CAPTION if qr_url else ""
    number = str(number or "")
    alphabet = str(alphabet or "")
    serial = str(serial or "") if serial else ""

    objekt.theme = ObjektTheme(
        text_color=text_color,
        background_color=background_color,
    )
    objekt.meta = ObjektMeta(
        artist_name=member or "",
        group_name=artist or "",
        number=number,
        alphabet=alphabet,
        serial=serial or None,
    )
    objekt.set_group_logo_side(side_logo_img)

    objekt.sidebar_img = objekt.make_sidebar_text_layer(
        use_background=True,
        include_serial=bool(number),
        base_img=sidebar_img,
    )
    objekt.front.set_sidebar_img(objekt.sidebar_img).attach_sidebar()

    objekt.back(class_, season).reset().change_outline_color(outline_color).attach_layout(back_img).draw_text()
    if top_logo_img is not None:
        objekt.back.attach_top_logo(top_logo_img)
    if qr_url:
        objekt.back.attach_qr_code(qr_url, qr_caption, qr_logo_img)
    if sign_img is not None:
        objekt.back.attach_sign(
            _scale_image(sign_img, sign_scale),
            (_to_int(sign_x, 74), _to_int(sign_y, 1065)),
        )
    objekt.back.draw_sidebar()

    raw_values = [
        artist,
        season,
        class_,
        color_mode,
        background_color,
        text_color,
        outline_color,
        member,
        number,
        alphabet,
        serial,
        qr_url,
    ]
    data = {
        "artist": {
            "name": member or "",
            "group": artist or "",
        },
        "appearance": {
            "background_color": appearance_background,
            "text_color": text_color,
            "outline_color": outline_color,
        },
        "identifiers": {
            "number": number,
            "alphabet": alphabet,
            "serial": serial if serial else None,
        },
        "text_area": {
            "class": class_,
            "season": season,
            "qr_code": qr_url,
            "qr_caption": qr_caption,
        },
        "raw": raw_values,
        "generation": {
            "started_at_epoch_us": time.time_ns() // 1_000,
            "timezone": "Asia/Seoul",
        },
    }
    meta_dict = {
        "artist": str(artist),
        "season": str(season),
        "class": str(class_),
        "member": str(member),
        "numbering_state": str(bool(number)),
        "number": str(number),
        "alphabet": str(alphabet),
        "serial": str(serial),
        "qr_code": str(qr_url),
        "outline_color": str(outline_color),
    }

    if cache_id:
        _remove_cached_images(cache_id)
    cache_id = get_kr_time()
    save_log_json(data, temp_id, f"{cache_id}.json")

    front_path, back_path, combined_path = _save_images(objekt, cache_id, meta_dict)
    return [
        objekt,
        temp_id,
        cache_id,
        [front_path, back_path, combined_path],
        gr.DownloadButton(value=front_path),
        gr.DownloadButton(value=back_path),
        gr.DownloadButton(value=combined_path),
        front_path,
        back_path,
        combined_path,
    ]


def _update_simple_objekt(
    objekt: Optional[Objekt],
    temp_id: Optional[str],
    cache_id: Optional[str],
    gallery_value: Any,
    artist: Optional[str],
    season: Optional[str],
    class_: Optional[str],
    background_color: Optional[str],
    text_color: Optional[str],
    member: Optional[str],
    unit: Any,
    numbering_state: Optional[bool],
    number: Optional[str],
    alphabet: Optional[str],
    serial: Optional[str],
    qr_code: Optional[str],
    force_gallery: bool,
) -> list[Any]:
    if not artist:
        return _empty_outputs(objekt, temp_id, cache_id, gallery_value)

    temp_id = temp_id or get_kr_time()
    resolved = resolve_artist_config(
        artist,
        member,
        season,
        class_,
        background_color,
        text_color,
    )

    member_text = _member_text(member, unit, class_)
    raw_values = [
        artist,
        season,
        class_,
        member,
        unit,
        numbering_state,
        number,
        alphabet,
        serial,
        qr_code,
    ]

    if not numbering_state:
        number = ""
        alphabet = ""
        serial = ""

    qr_url = DEFAULT_QR_CODE if qr_code is None else str(qr_code).strip()
    qr_caption = DEFAULT_QR_CAPTION if qr_url else ""

    if not isinstance(objekt, Objekt):
        objekt = Objekt(
            text_color=resolved.text_color,
            background_color=resolved.background_color,
            artist_name=member_text,
            group_name=resolved.group_name,
            number=number,
            alphabet=alphabet or "",
            serial=serial or None,
        )

    opened_gallery = open_gallery_image(gallery_value) if force_gallery else None
    if opened_gallery is not None:
        _copy_original_front_image(opened_gallery.source_path, temp_id)
        _set_front_image(objekt, opened_gallery.image)
        objekt._simple_raw_source = "user"
        objekt._simple_default_artist = None
    elif getattr(objekt, "_simple_raw_source", None) != "user":
        if resolved.default_image is not None and getattr(objekt, "_simple_default_artist", None) != artist:
            _set_front_image(objekt, resolved.default_image)
            objekt._simple_raw_source = "default"
            objekt._simple_default_artist = artist

    objekt.theme = ObjektTheme(
        text_color=resolved.text_color,
        background_color=resolved.background_color,
    )
    objekt.meta = ObjektMeta(
        artist_name=member_text,
        group_name=resolved.group_name,
        number=number,
        alphabet=alphabet or "",
        serial=serial or None,
    )
    objekt.set_group_logo_side(resolved.side_logo_img)

    include_serial = bool(number)
    objekt.sidebar_img = objekt.make_sidebar_text_layer(
        use_background=True,
        include_serial=include_serial,
        base_img=resolved.front_sidebar_img,
    )
    objekt.front.set_sidebar_img(objekt.sidebar_img).attach_sidebar()

    objekt.back(class_, resolved.season_display).reset().attach_layout(
        resolved.back_inside_img,
    ).draw_text()
    if resolved.top_logo_img is not None:
        objekt.back.attach_top_logo(resolved.top_logo_img)
    if qr_url:
        objekt.back.attach_qr_code(
            url=qr_url,
            caption=qr_caption,
            logo=resolved.qr_logo_img,
        )
    if resolved.sign_img is not None:
        objekt.back.attach_sign(resolved.sign_img, resolved.sign_position)
    objekt.back.draw_sidebar()

    sign_x, sign_y = resolved.sign_position or (74, 1065)
    objekt._simple_plus_snapshot = {
        "artist": resolved.group_name,
        "season": resolved.season_display,
        "class": class_,
        "color_mode": "Image"
        if resolved.front_sidebar_img is not None or resolved.back_inside_img is not None
        else "Static",
        "background_color": resolved.background_color,
        "text_color": resolved.text_color,
        "outline_color": "#FFFFFF",
        "member": member_text,
        "number": number,
        "alphabet": alphabet,
        "serial": serial,
        "qr_code": qr_url,
        "top_logo": resolved.top_logo_img,
        "side_logo": resolved.side_logo_img,
        "sign": resolved.sign_img,
        "sign_x": sign_x,
        "sign_y": sign_y,
        "sign_scale": 1,
        "qr_logo": resolved.qr_logo_img,
        "raw_sidebar": resolved.front_sidebar_img,
        "raw_back": resolved.back_inside_img,
    }

    started_at_epoch_us = time.time_ns() // 1_000
    data = {
        "artist": {
            "name": member_text,
            "group": resolved.group_name,
        },
        "appearance": {
            "background_color": resolved.appearance_background,
            "text_color": resolved.text_color,
        },
        "identifiers": {
            "number": number,
            "alphabet": alphabet,
            "serial": serial if serial else None,
        },
        "text_area": {
            "class": class_,
            "season": resolved.season_display,
            "qr_code": qr_url,
            "qr_caption": qr_caption,
        },
        "raw": raw_values,
        "generation": {
            "started_at_epoch_us": started_at_epoch_us,
            "timezone": "Asia/Seoul",
        },
    }

    meta_dict = {
        "artist": str(artist),
        "season": str(season),
        "class": str(class_),
        "member": str(member_text),
        "numbering_state": str(numbering_state),
        "number": str(number),
        "alphabet": str(alphabet),
        "serial": str(serial),
        "qr_code": str(qr_url),
    }

    if cache_id:
        _remove_cached_images(cache_id)
    cache_id = get_kr_time()
    save_log_json(data, temp_id, f"{cache_id}.json")

    front_path, back_path, combined_path = _save_images(objekt, cache_id, meta_dict)
    gallery = [front_path, back_path, combined_path]
    return [
        objekt,
        temp_id,
        cache_id,
        gallery,
        gr.DownloadButton(value=front_path),
        gr.DownloadButton(value=back_path),
        gr.DownloadButton(value=combined_path),
        front_path,
        back_path,
        combined_path,
    ]


def _gallery_items(gallery_value: Any) -> list[str]:
    if gallery_value is None:
        return []
    if isinstance(gallery_value, (str, Path)):
        return [str(gallery_value)]
    if isinstance(gallery_value, dict):
        path = gallery_value.get("path") or gallery_value.get("name")
        return [str(path)] if path else []
    if not isinstance(gallery_value, (list, tuple)):
        return []

    items = []
    for item in gallery_value:
        path = _gallery_item_path(item)
        if path:
            items.append(path)
    return items


def _gallery_item_path(item: Any) -> Optional[str]:
    if isinstance(item, (str, Path)):
        return str(item)
    if isinstance(item, dict):
        path = item.get("path") or item.get("name")
        return str(path) if path else None
    if isinstance(item, (list, tuple)) and item:
        return _gallery_item_path(item[0])
    return None


def _load_artist_image(artist: str, *parts: str) -> Optional[Image.Image]:
    path = ARTIST_DIR / artist / Path(*parts)
    if not path.exists():
        return None
    with Image.open(path) as img:
        return img.convert("RGBA").copy()


def _coerce_image(value: Any) -> Optional[Image.Image]:
    if value is None:
        return None
    if isinstance(value, Image.Image):
        return value.convert("RGBA").copy()
    if isinstance(value, dict):
        value = value.get("path") or value.get("name")
    if isinstance(value, (list, tuple)) and value:
        value = value[0]
    if isinstance(value, (str, Path)) and Path(value).exists():
        with Image.open(value) as img:
            return img.convert("RGBA").copy()
    return None


def _scale_image(image: Image.Image, scale: Any) -> Image.Image:
    scale_value = _to_float(scale, 1)
    if scale_value == 1:
        return image

    width = max(1, round(image.size[0] * scale_value))
    height = max(1, round(image.size[1] * scale_value))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def _to_int(value: Any, default: int) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _copy_original_front_image(source_path: Optional[Path], temp_id: str) -> Optional[Path]:
    if source_path is None:
        return None

    source_path = Path(source_path)
    if not source_path.is_file():
        return None

    log_dir = Path("logs") / str(temp_id)
    suffix = source_path.suffix
    target_path = log_dir / f"front-original{suffix}"

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
    except OSError:
        return None

    return target_path


def _set_front_image(objekt: Objekt, image: Image.Image) -> None:
    objekt.front.set_raw_img(image).resize().round_corner()


def _member_text(member: Optional[str], unit: Any, class_: Optional[str]) -> str:
    if class_ != "Unit":
        return member or ""
    if isinstance(unit, (list, tuple)):
        return " X ".join(str(value) for value in unit if value)
    return str(unit or "")


def _remove_cached_images(cache_id: str) -> None:
    safe_name = Path(str(cache_id)).name
    for suffix in ("objektify-front-", "objektify-back-", "objektify-combined-"):
        path = CACHE_DIR / f"{suffix}{safe_name}.png"
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def _save_images(
    objekt: Objekt,
    cache_id: str,
    meta_dict: dict[str, str],
) -> tuple[str, str, str]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    front = objekt.front.image()
    back = objekt.back.image()
    combined = Image.new(
        "RGBA",
        (front.size[0] + back.size[0], max(front.size[1], back.size[1])),
        (0, 0, 0, 0),
    )
    combined = paste_correctly(combined, (0, 0), front)
    combined = paste_correctly(combined, (front.size[0], 0), back)

    front_path = CACHE_DIR / f"objektify-front-{cache_id}.png"
    back_path = CACHE_DIR / f"objektify-back-{cache_id}.png"
    combined_path = CACHE_DIR / f"objektify-combined-{cache_id}.png"

    front.save(front_path, pnginfo=_png_meta(meta_dict, "front"))
    back.save(back_path, pnginfo=_png_meta(meta_dict, "back", mode="simple"))
    combined.save(combined_path, pnginfo=_png_meta(meta_dict, "both", mode="simple"))

    return front_path.as_posix(), back_path.as_posix(), combined_path.as_posix()


def _png_meta(
    meta_dict: dict[str, str],
    aspect: str,
    mode: Optional[str] = None,
) -> PngImagePlugin.PngInfo:
    meta = PngImagePlugin.PngInfo()
    meta.add_text("objektify", "V3")
    meta.add_text("aspect", aspect)
    if mode is not None:
        meta.add_text("mode", mode)
    for key, value in meta_dict.items():
        meta.add_text(key, value)
    return meta


def _empty_outputs(
    objekt: Optional[Objekt],
    temp_id: Optional[str],
    cache_id: Optional[str],
    gallery_value: Any,
) -> list[Any]:
    return [
        objekt,
        temp_id,
        cache_id,
        gallery_value,
        gr.DownloadButton(value=None),
        gr.DownloadButton(value=None),
        gr.DownloadButton(value=None),
        None,
        None,
        None,
    ]
