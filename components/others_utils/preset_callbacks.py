from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import gradio as gr
from PIL import Image

from config import ARTIST_DIR
from generate.modhaus.preset import Preset, PresetMember
from utils import (
    color_change as recolor_image,
    crop_transparent_padding,
    list_artist_folders,
    paste_correctly,
    remove_signature_background,
    resize_keep_ratio,
    rgba_to_hex,
    svg_to_pil,
)
from utils.logo_upload import qr as qr_logo_upload
from utils.logo_upload import side as side_logo_upload
from utils.logo_upload import top as top_logo_upload

from .make_default_preview import make_default_preview
from .sign_upload import composit_preview, fit_image, svg_to_rgba_array


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESOURCE_DIR = PROJECT_ROOT / "utils" / "resources"
SIGN_STATUS_HEADERS = ["Member", "Uploaded", "Position", "Updated"]


def preset_debug_config(preset: Optional[Preset]) -> dict[str, Any]:
    if not isinstance(preset, Preset):
        return Preset.new().to_config()
    return preset.to_config()


def status_markdown(preset: Optional[Preset]) -> str:
    if not isinstance(preset, Preset):
        preset = Preset.new()

    season_count = len(preset.seasons)
    class_count = sum(
        len([key for key in season.keys() if key != "display"])
        for season in preset.seasons.values()
    )
    sign_count = sum(
        1
        for name, member in preset.members.items()
        if member.sign and name in preset.assets.signs
    )
    folder = preset.folder_name if preset.name and preset.creator_name else preset.source_folder or "-"
    save_ready = "Yes" if preset.name and preset.creator_name and preset.members and preset.all_seasons_have_class() else "No"

    return "\n".join(
        [
            f"### {preset.name or 'Untitled preset'}",
            f"- Folder: `{folder}`",
            f"- Creator: `{preset.creator_name or '-'}`",
            f"- Members: {len(preset.members)}",
            f"- Seasons / Classes: {season_count} / {class_count}",
            f"- Signs: {sign_count} / {len(preset.members)}",
            f"- Logos: top={_yesno(preset.has_top_logo)}, qr={_yesno(preset.has_qr_logo)}, side={_yesno(preset.has_side_logo)}",
            f"- Default image: {_yesno(preset.has_default_img)}",
            f"- Basic save readiness: {save_ready}",
        ]
    )


def sign_status_rows(preset: Optional[Preset]) -> list[list[Any]]:
    if not isinstance(preset, Preset):
        return []
    return preset.sign_status_rows()


def panel_outputs(preset: Optional[Preset]) -> tuple[gr.Markdown, gr.Dataframe, gr.JSON]:
    return (
        gr.Markdown(value=status_markdown(preset)),
        gr.Dataframe(value=sign_status_rows(preset), headers=SIGN_STATUS_HEADERS),
        gr.JSON(value=preset_debug_config(preset)),
    )


def community_preset_dropdown() -> gr.Dropdown:
    return gr.Dropdown(choices=list_artist_folders(False), value=None)


def toggle_start_mode(mode: str) -> tuple[gr.Group, gr.Button, gr.Button, gr.Dropdown]:
    is_edit = mode == "Edit Existing"
    return (
        gr.Group(visible=is_edit),
        gr.Button(visible=not is_edit, variant="primary"),
        gr.Button(visible=is_edit, variant="primary"),
        gr.Dropdown(choices=list_artist_folders(False)),
    )


def create_new_preset():
    preset = Preset.new()
    status, signs, config = panel_outputs(preset)
    return (
        preset,
        gr.Textbox(value=""),
        gr.Dropdown(choices=[], value=[], multiselect=True, allow_custom_value=True),
        gr.Dropdown(choices=[], value=[], multiselect=True, allow_custom_value=True),
        gr.Radio(choices=[], value=None),
        gr.Dropdown(choices=[], value=[], multiselect=True, allow_custom_value=True),
        gr.Radio(choices=[], value=None),
        gr.Radio(choices=[], value=None),
        gr.Textbox(value=""),
        gr.Textbox(value=""),
        gr.Textbox(value=""),
        gr.ColorPicker(value="#FFFFFF"),
        gr.ColorPicker(value="#000000"),
        gr.Image(value=_resource("top_logo_preview.png")),
        gr.Image(value=_resource("qr_logo_preview.png")),
        gr.Image(value=None),
        gr.Image(value=_resource("front_preview.png")),
        gr.Button(interactive=False, variant="secondary"),
        status,
        signs,
        config,
        gr.Walkthrough(selected=1),
    )


def load_existing_preset(current: Optional[Preset], folder: str, password: str):
    if not folder:
        gr.Info("Select a preset to edit.")
        return _load_no_update(current)

    preset = Preset.from_artist_dir(folder)
    if preset.official:
        gr.Info("Official presets are read-only in this editor.")
        return _load_no_update(current)

    if not preset.verify_password(password or ""):
        gr.Info("Password does not match.")
        return _load_no_update(current)

    add_seasons = _season_displays(preset)
    season_keys = list(preset.seasons.keys())
    selected_season = season_keys[0] if season_keys else None
    class_values = _classes_for_season(preset, selected_season)
    selected_class = class_values[0] if class_values else None
    default_side, default_text = _default_colors(preset)
    default_preview, _ = make_default_preview(default_side, default_text, preset.assets.default_img, "Center of container")

    status, signs, config = panel_outputs(preset)
    return (
        preset,
        gr.Textbox(value=preset.name),
        gr.Dropdown(choices=list(preset.members.keys()), value=list(preset.members.keys()), multiselect=True, allow_custom_value=True),
        gr.Dropdown(choices=add_seasons, value=add_seasons, multiselect=True, allow_custom_value=True),
        gr.Radio(choices=season_keys, value=selected_season),
        gr.Dropdown(choices=class_values, value=class_values, multiselect=True, allow_custom_value=True),
        gr.Radio(choices=class_values, value=selected_class),
        gr.Radio(choices=list(preset.members.keys()), value=list(preset.members.keys())[0] if preset.members else None),
        gr.Textbox(value=preset.creator_name),
        gr.Textbox(value=preset.contact.get("discord")),
        gr.Textbox(value=preset.contact.get("email")),
        gr.ColorPicker(value=default_side),
        gr.ColorPicker(value=default_text),
        gr.Image(value=_top_preview(preset.assets.top_logo)),
        gr.Image(value=_qr_preview(preset.assets.qr_logo)),
        gr.Image(value=_side_preview(preset.assets.side_logo)),
        gr.Image(value=default_preview),
        _artist_next_button(preset),
        status,
        signs,
        config,
        gr.Walkthrough(selected=1),
    )


def set_identity(preset: Optional[Preset], group: str, members: list[str] | None):
    preset = _preset(preset)
    preset.name = group or ""
    preset.set_members(members)
    status, signs, config = panel_outputs(preset)
    return (
        preset,
        _artist_next_button(preset),
        gr.Radio(choices=list(preset.members.keys()), value=list(preset.members.keys())[0] if preset.members else None),
        status,
        signs,
        config,
    )


def set_seasons(preset: Optional[Preset], seasons: list[str] | None):
    preset = _preset(preset)
    preset.set_seasons_from_display(seasons)
    season_keys = list(preset.seasons.keys())
    selected_season = season_keys[0] if season_keys else None
    class_values = _classes_for_season(preset, selected_season)
    status, signs, config = panel_outputs(preset)
    return (
        preset,
        gr.Button(interactive=bool(season_keys), variant="primary" if season_keys else "secondary"),
        gr.Radio(choices=season_keys, value=selected_season),
        gr.Dropdown(choices=class_values, value=class_values, multiselect=True, allow_custom_value=True),
        gr.Radio(choices=class_values, value=class_values[0] if class_values else None),
        status,
        signs,
        config,
    )


def select_season(preset: Optional[Preset], season_key: Optional[str]):
    preset = _preset(preset)
    class_values = _classes_for_season(preset, season_key)
    selected_class = class_values[0] if class_values else None
    bc, tc = _class_colors(preset, season_key, selected_class)
    return (
        gr.Dropdown(choices=class_values, value=class_values, multiselect=True, allow_custom_value=True),
        gr.Radio(choices=class_values, value=selected_class),
        gr.ColorPicker(value=bc),
        gr.ColorPicker(value=tc),
    )


def set_classes(preset: Optional[Preset], season_key: Optional[str], class_names: list[str] | None, bc: str, tc: str):
    preset = _preset(preset)
    preset.set_classes(season_key, class_names, (rgba_to_hex(bc), rgba_to_hex(tc)))
    class_values = _classes_for_season(preset, season_key)
    selected_class = class_values[0] if class_values else None
    status, signs, config = panel_outputs(preset)
    return (
        preset,
        gr.Radio(choices=class_values, value=selected_class),
        gr.Button(interactive=preset.all_seasons_have_class(), variant="primary" if preset.all_seasons_have_class() else "secondary"),
        status,
        signs,
        config,
    )


def select_class(preset: Optional[Preset], season_key: Optional[str], class_name: Optional[str]):
    preset = _preset(preset)
    bc, tc = _class_colors(preset, season_key, class_name)
    return gr.ColorPicker(value=bc), gr.ColorPicker(value=tc)


def set_class_color(preset: Optional[Preset], season_key: Optional[str], class_name: Optional[str], bc: str, tc: str):
    preset = _preset(preset)
    if not season_key or not class_name:
        gr.Info("Select a season and class first.")
        status, signs, config = panel_outputs(preset)
        return preset, status, signs, config

    preset.seasons.setdefault(season_key, {"display": season_key})[class_name] = [rgba_to_hex(bc), rgba_to_hex(tc)]
    status, signs, config = panel_outputs(preset)
    return preset, status, signs, config


def select_sign_member(preset: Optional[Preset], member_name: Optional[str]):
    preset = _preset(preset)
    preview = None
    x_offset = 0
    y_offset = 0
    size = 100

    if member_name and member_name in preset.assets.signs:
        sign = preset.assets.signs[member_name]
        member = preset.members.get(member_name)
        position = member.position if member else None
        if position:
            x_offset = int(position[0] - (68 + ((436 - sign.size[0]) / 2)))
            y_offset = int(position[1] - (1030 + ((293 - sign.size[1]) / 2)))
        preview = _sign_preview(sign, position)

    return (
        gr.Image(value=preview),
        gr.Slider(value=x_offset),
        gr.Slider(value=y_offset),
        gr.Slider(value=size),
    )


def apply_sign(
    preset: Optional[Preset],
    member_name: Optional[str],
    file: str,
    x_offset: float,
    y_offset: float,
    size: int,
    remove_bg: bool,
):
    preset = _preset(preset)
    if not member_name:
        gr.Info("Select a member first.")
        status, signs, config = panel_outputs(preset)
        return preset, gr.Image(value=None), status, signs, config
    if not file:
        gr.Info("Upload a sign file first.")
        status, signs, config = panel_outputs(preset)
        return preset, gr.Image(value=None), status, signs, config

    sign = _read_sign(file, size, remove_bg)
    preview_base, position = composit_preview(sign, x_offset, y_offset)
    preview = preview_base.crop((0, 797, 1083, 729 + 797))

    preset.assets.signs[member_name] = sign
    member = preset.members.setdefault(member_name, PresetMember(name=member_name))
    member.sign = True
    member.position = (int(position[0]), int(position[1]))
    member.updated_at = "just now"

    status, signs, config = panel_outputs(preset)
    return preset, gr.Image(value=preview), status, signs, config


def set_top_logo(preset: Optional[Preset], file: str, scale: int, remove_bg: bool):
    preset = _preset(preset)
    file = _path_value(file)
    preview, image, _ = top_logo_upload({}, file, scale, remove_bg)
    preset.assets.top_logo = _pil_or_none(image)
    status, signs, config = panel_outputs(preset)
    return preset, preview, status, signs, config


def set_qr_logo(preset: Optional[Preset], file: str):
    preset = _preset(preset)
    file = _path_value(file)
    preview, image, _ = qr_logo_upload({}, file)
    preset.assets.qr_logo = _pil_or_none(image)
    status, signs, config = panel_outputs(preset)
    return preset, preview, status, signs, config


def set_side_logo(preset: Optional[Preset], file: str, scale: int, remove_bg: bool):
    preset = _preset(preset)
    file = _path_value(file)
    preview, image, _ = side_logo_upload({}, file, scale, remove_bg)
    preset.assets.side_logo = _pil_or_none(image)
    status, signs, config = panel_outputs(preset)
    return preset, preview, status, signs, config


def set_default(
    preset: Optional[Preset],
    default_color_side: str,
    default_color_text: str,
    default_img: Optional[Image.Image],
    batch_type: str,
):
    preset = _preset(preset)
    preview, save_image = make_default_preview(default_color_side, default_color_text, default_img, batch_type)
    preset.default_color = [default_color_side or "#FFFFFF", default_color_text or "#000000"]
    preset.assets.default_img = save_image.convert("RGBA").copy() if save_image else None
    status, signs, config = panel_outputs(preset)
    return preset, preview, status, signs, config


def submit_preset(
    preset: Optional[Preset],
    creator_name: str,
    password: str,
    password_confirm: str,
    discord_id: str,
    email_id: str,
    default_color_side: str,
    default_color_text: str,
):
    preset = _preset(preset)
    preset.creator_name = creator_name or ""
    preset.contact = {"discord": discord_id, "email": email_id}
    preset.default_color = [default_color_side or "#FFFFFF", default_color_text or "#000000"]

    try:
        path = preset.save(password=password or None, password_confirm=password_confirm or None)
    except Exception as exc:
        result = gr.Markdown(value=f"### Save failed\n{exc}")
        status, signs, config = panel_outputs(preset)
        return preset, result, community_preset_dropdown(), status, signs, config

    result = gr.Markdown(value=f"### Saved!")
    status, signs, config = panel_outputs(preset)
    return preset, result, community_preset_dropdown(), status, signs, config


def _load_no_update(current: Optional[Preset]):
    preset = _preset(current)
    status, signs, config = panel_outputs(preset)
    return (
        preset,
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        _artist_next_button(preset),
        status,
        signs,
        config,
        gr.Walkthrough(selected=0),
    )


def _preset(preset: Optional[Preset]) -> Preset:
    return preset if isinstance(preset, Preset) else Preset.new()


def _artist_next_button(preset: Preset) -> gr.Button:
    ready = bool(preset.name and preset.members)
    return gr.Button(interactive=ready, variant="primary" if ready else "secondary")


def _season_displays(preset: Preset) -> list[str]:
    return [season.get("display", key) for key, season in preset.seasons.items()]


def _classes_for_season(preset: Preset, season_key: Optional[str]) -> list[str]:
    if not season_key:
        return []
    season = preset.seasons.get(season_key, {})
    return [key for key in season.keys() if key != "display"]


def _class_colors(preset: Preset, season_key: Optional[str], class_name: Optional[str]) -> tuple[str, str]:
    if not season_key or not class_name:
        return "#FFFFFF", "#000000"
    value = preset.seasons.get(season_key, {}).get(class_name)
    if not isinstance(value, list) or len(value) < 2:
        return "#FFFFFF", "#000000"
    return value[0], value[1]


def _default_colors(preset: Preset) -> tuple[str, str]:
    if len(preset.default_color) >= 2:
        return preset.default_color[0], preset.default_color[1]
    return "#FFFFFF", "#000000"


def _read_sign(file: str, size: int, remove_bg: bool) -> Image.Image:
    file = _path_value(file)
    if not file:
        raise ValueError("No sign file was provided.")

    suffix = Path(file).suffix.lower()
    if suffix in {".png", ".jpeg", ".jpg", ".webp"}:
        source = Image.open(file) if not remove_bg else remove_signature_background(file)
        return fit_image(crop_transparent_padding(source), size)
    if suffix == ".svg":
        return fit_image(svg_to_rgba_array(file), size)
    raise ValueError(f"Unknown sign file type: {suffix}")


def _path_value(file: Any) -> Optional[str]:
    if not file:
        return None
    if isinstance(file, (str, Path)):
        return str(file)
    if isinstance(file, dict):
        path = file.get("path") or file.get("name")
        return str(path) if path else None
    if isinstance(file, (list, tuple)) and file:
        return _path_value(file[0])
    path = getattr(file, "path", None) or getattr(file, "name", None)
    return str(path) if path else str(file)


def _sign_preview(sign: Image.Image, position: Optional[tuple[int, int]]) -> Optional[Image.Image]:
    if position is None:
        preview, _ = composit_preview(sign, 0, 0)
    else:
        base = Image.open(PROJECT_ROOT / "components" / "others_utils" / "resources" / "preview.png").convert("RGBA")
        preview = paste_correctly(base, position, recolor_image(sign, "#FFFFFF"))
    return preview.crop((0, 797, 1083, 729 + 797))


def _pil_or_none(value: Any) -> Optional[Image.Image]:
    return value.convert("RGBA").copy() if isinstance(value, Image.Image) else None


def _resource(filename: str) -> str:
    return str(RESOURCE_DIR / filename)


def _top_preview(image: Optional[Image.Image]) -> str | Image.Image:
    if image is None:
        return _resource("top_logo_preview.png")
    base = Image.open(RESOURCE_DIR / "top_logo_preview.png").convert("RGBA")
    return paste_correctly(base, (57, 151), image.convert("RGBA"))


def _qr_preview(image: Optional[Image.Image]) -> str | Image.Image:
    if image is None:
        return _resource("qr_logo_preview.png")
    base = Image.open(RESOURCE_DIR / "qr_logo_preview.png").convert("RGBA")
    return paste_correctly(base, (235, 157), image.convert("RGBA"))


def _side_preview(image: Optional[Image.Image]) -> Optional[Image.Image]:
    if image is None:
        return None
    base = Image.open(RESOURCE_DIR / "side_logo_preview.png").convert("RGBA")
    rotated = image.convert("RGBA").rotate(270, expand=True)
    return paste_correctly(
        base,
        (base.size[0] - 37 - rotated.size[0], base.size[1] - 152 - rotated.size[1]),
        rotated,
    )


def _yesno(value: bool) -> str:
    return "yes" if value else "no"
