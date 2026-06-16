from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import gradio as gr
from PIL import Image

from config import ARTIST_DIR
from generate.modhaus.preset import Preset, PresetLayoutAsset, PresetMember, is_valid_layout_asset_key
from utils import (
    color_change as recolor_image,
    crop_transparent_padding,
    list_artist_folders,
    paste_correctly,
    remove_signature_background,
    rgba_to_hex,
)
from utils.logo_upload import qr as qr_logo_upload
from utils.logo_upload import side as side_logo_upload
from utils.logo_upload import top as top_logo_upload

from .make_default_preview import make_default_preview
from .sign_upload import composit_preview, fit_image, svg_to_rgba_array


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESOURCE_DIR = PROJECT_ROOT / "utils" / "resources"
SIGN_STATUS_HEADERS = ["Member", "Uploaded", "Position", "Updated"]
BACKGROUND_SOURCE_STATIC = "Static Color"
BACKGROUND_SOURCE_CHOOSE = "User Choose (@choose)"
BACKGROUND_SOURCE_LAYOUT = "Layout Asset"
BACKGROUND_SOURCE_CHOICES = [
    BACKGROUND_SOURCE_STATIC,
    BACKGROUND_SOURCE_CHOOSE,
    BACKGROUND_SOURCE_LAYOUT,
]
PLAIN_LAYOUT_ASSET_DEFAULTS = {"special", "premier"}


def layout_asset_dropdown_choices(preset: Optional[Preset] = None) -> list[str]:
    choices = _available_layout_asset_sources()
    if isinstance(preset, Preset):
        for key in sorted(preset.referenced_layout_asset_keys() | set(preset.assets.layout_assets.keys())):
            if key not in PLAIN_LAYOUT_ASSET_DEFAULTS and key not in choices:
                choices.append(key)
    return choices


def layout_asset_dropdown_value(preset: Optional[Preset] = None) -> Optional[str]:
    choices = layout_asset_dropdown_choices(preset)
    return choices[0] if choices else None


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
    layout_keys = sorted(preset.referenced_layout_asset_keys())
    layout_errors = preset.layout_asset_errors()
    sign_count = sum(
        1
        for name, member in preset.members.items()
        if member.sign and name in preset.assets.signs
    )
    folder = preset.folder_name if preset.name and preset.creator_name else preset.source_folder or "-"
    save_ready = (
        "Yes"
        if preset.name and preset.creator_name and preset.members and preset.all_seasons_have_class() and not layout_errors
        else "No"
    )

    return "\n".join(
        [
            f"### {preset.name or 'Untitled preset'}",
            f"- Folder: `{folder}`",
            f"- Creator: `{preset.creator_name or '-'}`",
            f"- Members: {len(preset.members)}",
            f"- Seasons / Classes: {season_count} / {class_count}",
            f"- Layout assets: {len(layout_keys)} ({len(layout_errors)} missing)",
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
        gr.Radio(choices=BACKGROUND_SOURCE_CHOICES, value=BACKGROUND_SOURCE_STATIC),
        gr.ColorPicker(value="#FFFFFF", visible=True),
        gr.Group(visible=False),
        gr.Dropdown(choices=layout_asset_dropdown_choices(), value=layout_asset_dropdown_value(), allow_custom_value=True),
        gr.Image(value=None, visible=True),
        gr.Image(value=None, visible=True),
        gr.ColorPicker(value="#000000", visible=True),
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
    source, bc, asset_key, front_layout, back_layout, tc = _class_appearance(preset, selected_season, selected_class)
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
        gr.Radio(choices=BACKGROUND_SOURCE_CHOICES, value=source),
        gr.ColorPicker(value=bc, visible=source == BACKGROUND_SOURCE_STATIC),
        gr.Group(visible=source == BACKGROUND_SOURCE_LAYOUT),
        gr.Dropdown(choices=layout_asset_dropdown_choices(preset), value=asset_key, allow_custom_value=True),
        gr.Image(value=front_layout, visible=True),
        gr.Image(value=back_layout, visible=True),
        gr.ColorPicker(value=tc, visible=source == BACKGROUND_SOURCE_STATIC),
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
        _class_next_button(preset),
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
    selected_class = class_values[0] if class_values else None
    source, bc, asset_key, front_layout, back_layout, tc = _class_appearance(preset, selected_season, selected_class)
    status, signs, config = panel_outputs(preset)
    return (
        preset,
        gr.Button(interactive=bool(season_keys), variant="primary" if season_keys else "secondary"),
        gr.Radio(choices=season_keys, value=selected_season),
        gr.Dropdown(choices=class_values, value=class_values, multiselect=True, allow_custom_value=True),
        gr.Radio(choices=class_values, value=selected_class),
        gr.Radio(choices=BACKGROUND_SOURCE_CHOICES, value=source),
        gr.ColorPicker(value=bc, visible=source == BACKGROUND_SOURCE_STATIC),
        gr.Group(visible=source == BACKGROUND_SOURCE_LAYOUT),
        gr.Dropdown(choices=layout_asset_dropdown_choices(preset), value=asset_key, allow_custom_value=True),
        gr.Image(value=front_layout, visible=True),
        gr.Image(value=back_layout, visible=True),
        gr.ColorPicker(value=tc, visible=source == BACKGROUND_SOURCE_STATIC),
        _class_next_button(preset),
        status,
        signs,
        config,
    )


def select_season(preset: Optional[Preset], season_key: Optional[str]):
    preset = _preset(preset)
    class_values = _classes_for_season(preset, season_key)
    selected_class = class_values[0] if class_values else None
    source, bc, asset_key, front_layout, back_layout, tc = _class_appearance(preset, season_key, selected_class)
    return (
        gr.Dropdown(choices=class_values, value=class_values, multiselect=True, allow_custom_value=True),
        gr.Radio(choices=class_values, value=selected_class),
        gr.Radio(choices=BACKGROUND_SOURCE_CHOICES, value=source),
        gr.ColorPicker(value=bc, visible=source == BACKGROUND_SOURCE_STATIC),
        gr.Group(visible=source == BACKGROUND_SOURCE_LAYOUT),
        gr.Dropdown(choices=layout_asset_dropdown_choices(preset), value=asset_key, allow_custom_value=True),
        gr.Image(value=front_layout, visible=True),
        gr.Image(value=back_layout, visible=True),
        gr.ColorPicker(value=tc, visible=source == BACKGROUND_SOURCE_STATIC),
    )


def set_classes(
    preset: Optional[Preset],
    season_key: Optional[str],
    class_names: list[str] | None,
    background_source: str,
    asset_key: str,
    bc: str,
    tc: str,
):
    preset = _preset(preset)
    preset.set_classes(season_key, class_names, _default_class_spec(background_source, asset_key, bc, tc))
    if _normalize_background_source(background_source) == BACKGROUND_SOURCE_LAYOUT:
        token, source_asset, _ = _layout_asset_selection(asset_key)
        if token and source_asset is not None:
            preset.assets.layout_assets[token] = source_asset
    class_values = _classes_for_season(preset, season_key)
    selected_class = class_values[0] if class_values else None
    source, selected_bc, selected_asset_key, front_layout, back_layout, selected_tc = _class_appearance(preset, season_key, selected_class)
    if source == BACKGROUND_SOURCE_LAYOUT and _valid_layout_asset_selection(asset_key):
        selected_asset_key = asset_key
    status, signs, config = panel_outputs(preset)
    return (
        preset,
        gr.Radio(choices=class_values, value=selected_class),
        gr.Radio(choices=BACKGROUND_SOURCE_CHOICES, value=source),
        gr.ColorPicker(value=selected_bc, visible=source == BACKGROUND_SOURCE_STATIC),
        gr.Group(visible=source == BACKGROUND_SOURCE_LAYOUT),
        gr.Dropdown(choices=layout_asset_dropdown_choices(preset), value=selected_asset_key, allow_custom_value=True),
        gr.Image(value=front_layout, visible=True),
        gr.Image(value=back_layout, visible=True),
        gr.ColorPicker(value=selected_tc, visible=source == BACKGROUND_SOURCE_STATIC),
        _class_next_button(preset),
        status,
        signs,
        config,
    )


def select_class(preset: Optional[Preset], season_key: Optional[str], class_name: Optional[str]):
    preset = _preset(preset)
    source, bc, asset_key, front_layout, back_layout, tc = _class_appearance(preset, season_key, class_name)
    return (
        gr.Radio(choices=BACKGROUND_SOURCE_CHOICES, value=source),
        gr.ColorPicker(value=bc, visible=source == BACKGROUND_SOURCE_STATIC),
        gr.Group(visible=source == BACKGROUND_SOURCE_LAYOUT),
        gr.Dropdown(choices=layout_asset_dropdown_choices(preset), value=asset_key, allow_custom_value=True),
        gr.Image(value=front_layout, visible=True),
        gr.Image(value=back_layout, visible=True),
        gr.ColorPicker(value=tc, visible=source == BACKGROUND_SOURCE_STATIC),
    )


def set_class_source(
    preset: Optional[Preset],
    season_key: Optional[str],
    class_name: Optional[str],
    background_source: str,
    asset_key: str,
    bc: str,
    tc: str,
):
    return _set_class_appearance(
        preset,
        season_key,
        class_name,
        background_source,
        asset_key,
        bc,
        tc,
        front_layout=None,
        back_layout=None,
        update_layout_images=False,
    )


def set_class_appearance(
    preset: Optional[Preset],
    season_key: Optional[str],
    class_name: Optional[str],
    background_source: str,
    asset_key: str,
    bc: str,
    tc: str,
    front_layout: Any,
    back_layout: Any,
):
    return _set_class_appearance(
        preset,
        season_key,
        class_name,
        background_source,
        asset_key,
        bc,
        tc,
        front_layout=front_layout,
        back_layout=back_layout,
        update_layout_images=True,
    )


def set_class_layout_images(
    preset: Optional[Preset],
    season_key: Optional[str],
    class_name: Optional[str],
    background_source: str,
    asset_key: str,
    bc: str,
    tc: str,
    front_layout: Any,
    back_layout: Any,
):
    preset = _preset(preset)
    if not season_key or not class_name:
        gr.Info("Select a season and class first.")
        status, signs, config = panel_outputs(preset)
        return preset, _class_next_button(preset), status, signs, config

    source = _normalize_background_source(background_source)
    if source != BACKGROUND_SOURCE_LAYOUT:
        status, signs, config = panel_outputs(preset)
        return preset, _class_next_button(preset), status, signs, config

    token, _, source_text_color = _layout_asset_selection(asset_key)
    if token is None:
        gr.Info("Layout asset key must use only A-Z, a-z, 0-9, _ or -.")
        status, signs, config = panel_outputs(preset)
        return preset, _class_next_button(preset), status, signs, config

    text_color = source_text_color or _normalize_color(tc, "#000000")
    asset = preset.assets.layout_assets.setdefault(token, PresetLayoutAsset())
    front_image = _image_value(front_layout)
    back_image = _image_value(back_layout)
    if front_image is not None:
        asset.front = front_image
    if back_image is not None:
        asset.back = back_image

    preset.seasons.setdefault(season_key, {"display": season_key})[class_name] = [token, text_color]
    status, signs, config = panel_outputs(preset)
    return preset, _class_next_button(preset), status, signs, config


def _set_class_appearance(
    preset: Optional[Preset],
    season_key: Optional[str],
    class_name: Optional[str],
    background_source: str,
    asset_key: str,
    bc: str,
    tc: str,
    front_layout: Any,
    back_layout: Any,
    update_layout_images: bool,
):
    preset = _preset(preset)
    if not season_key or not class_name:
        gr.Info("Select a season and class first.")
        status, signs, config = panel_outputs(preset)
        source = _normalize_background_source(background_source)
        return _class_appearance_outputs(preset, source, bc, asset_key, None, None, tc, status, signs, config)

    source = _normalize_background_source(background_source)
    selected_asset_value = asset_key
    text_color = _normalize_color(tc, "#000000")
    background_color = _normalize_color(bc, "#FFFFFF")

    if source == BACKGROUND_SOURCE_CHOOSE:
        token = "@choose"
        text_color = "#000000"
    elif source == BACKGROUND_SOURCE_LAYOUT:
        token, source_asset, source_text_color = _layout_asset_selection(asset_key)
        if token is None:
            gr.Info("Layout asset key must use only A-Z, a-z, 0-9, _ or -.")
            source, background_color, token, front_layout, back_layout, text_color = _class_appearance(
                preset,
                season_key,
                class_name,
            )
            status, signs, config = panel_outputs(preset)
            return _class_appearance_outputs(
                preset,
                source,
                background_color,
                token,
                front_layout,
                back_layout,
                text_color,
                status,
                signs,
                config,
            )

        asset = preset.assets.layout_assets.setdefault(token, PresetLayoutAsset())
        if source_asset is not None:
            asset.front = source_asset.front
            asset.back = source_asset.back
            text_color = source_text_color or "#000000"
            selected_asset_value = str(asset_key).strip()
        else:
            selected_asset_value = token
        if update_layout_images:
            front_image = _image_value(front_layout)
            back_image = _image_value(back_layout)
            if front_image is not None:
                asset.front = front_image
            if back_image is not None:
                asset.back = back_image
        front_layout = asset.front
        back_layout = asset.back
    else:
        token = background_color

    preset.seasons.setdefault(season_key, {"display": season_key})[class_name] = [token, text_color]

    status, signs, config = panel_outputs(preset)
    return _class_appearance_outputs(preset, source, background_color, selected_asset_value, front_layout, back_layout, text_color, status, signs, config)


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
        *[gr.update() for _ in range(23)],
        _artist_next_button(preset),
        _class_next_button(preset),
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


def _class_next_button(preset: Preset) -> gr.Button:
    ready = preset.all_seasons_have_class() and not preset.layout_asset_errors()
    return gr.Button(interactive=ready, variant="primary" if ready else "secondary")


def _season_displays(preset: Preset) -> list[str]:
    return [season.get("display", key) for key, season in preset.seasons.items()]


def _classes_for_season(preset: Preset, season_key: Optional[str]) -> list[str]:
    if not season_key:
        return []
    season = preset.seasons.get(season_key, {})
    return [key for key in season.keys() if key != "display"]


def _class_appearance(
    preset: Preset,
    season_key: Optional[str],
    class_name: Optional[str],
) -> tuple[str, str, str, Optional[Image.Image], Optional[Image.Image], str]:
    default_asset_key = layout_asset_dropdown_value(preset) or ""
    if not season_key or not class_name:
        return BACKGROUND_SOURCE_STATIC, "#FFFFFF", default_asset_key, None, None, "#000000"

    value = preset.seasons.get(season_key, {}).get(class_name)
    if not isinstance(value, list) or len(value) < 2:
        return BACKGROUND_SOURCE_STATIC, "#FFFFFF", default_asset_key, None, None, "#000000"

    token = str(value[0]).strip()
    text_color = _normalize_color(value[1], "#000000")
    if token.startswith("#"):
        return BACKGROUND_SOURCE_STATIC, _normalize_color(token, "#FFFFFF"), default_asset_key, None, None, text_color
    if token == "@choose":
        return BACKGROUND_SOURCE_CHOOSE, "#FFFFFF", default_asset_key, None, None, text_color

    asset_key = token if token else default_asset_key
    asset = preset.assets.layout_assets.get(asset_key)
    return (
        BACKGROUND_SOURCE_LAYOUT,
        "#FFFFFF",
        asset_key,
        asset.front if asset else None,
        asset.back if asset else None,
        text_color,
    )


def _class_appearance_outputs(
    preset: Preset,
    background_source: str,
    bc: str,
    asset_key: Optional[str],
    front_layout: Optional[Image.Image],
    back_layout: Optional[Image.Image],
    tc: str,
    status: gr.Markdown,
    signs: gr.Dataframe,
    config: gr.JSON,
):
    source = _normalize_background_source(background_source)
    choices = layout_asset_dropdown_choices(preset)
    selected_asset_key = asset_key if _valid_layout_asset_selection(asset_key) else layout_asset_dropdown_value(preset)
    return (
        preset,
        gr.Radio(choices=BACKGROUND_SOURCE_CHOICES, value=source),
        gr.ColorPicker(value=_normalize_color(bc, "#FFFFFF"), visible=source == BACKGROUND_SOURCE_STATIC),
        gr.Group(visible=source == BACKGROUND_SOURCE_LAYOUT),
        gr.Dropdown(choices=choices, value=selected_asset_key, allow_custom_value=True),
        gr.Image(value=front_layout, visible=True),
        gr.Image(value=back_layout, visible=True),
        gr.ColorPicker(value=_normalize_color(tc, "#000000"), visible=source == BACKGROUND_SOURCE_STATIC),
        _class_next_button(preset),
        status,
        signs,
        config,
    )


def _default_class_spec(background_source: str, asset_key: str, bc: str, tc: str) -> tuple[str, str]:
    source = _normalize_background_source(background_source)
    text_color = _normalize_color(tc, "#000000")
    if source == BACKGROUND_SOURCE_CHOOSE:
        return "@choose", "#000000"
    if source == BACKGROUND_SOURCE_LAYOUT:
        token, _, source_text_color = _layout_asset_selection(asset_key)
        return token or "", source_text_color or "#000000"
    return _normalize_color(bc, "#FFFFFF"), text_color


def _normalize_background_source(value: str) -> str:
    return value if value in BACKGROUND_SOURCE_CHOICES else BACKGROUND_SOURCE_STATIC


def _valid_layout_asset_selection(value: Any) -> bool:
    token, _, _ = _layout_asset_selection(value)
    return token is not None


def _layout_asset_selection(value: Any) -> tuple[Optional[str], Optional[PresetLayoutAsset], Optional[str]]:
    raw_value = str(value or "").strip()
    if not raw_value:
        return None, None, None

    normalized = raw_value.replace("\\", "/")
    parts = normalized.split("/")
    if len(parts) == 2:
        artist_name, asset_key = parts
        if not _is_safe_path_name(artist_name) or not is_valid_layout_asset_key(asset_key):
            return None, None, None
        source_asset = _load_layout_asset_source(artist_name, asset_key)
        if source_asset is None:
            return None, None, None
        return asset_key, source_asset, _layout_asset_text_color(artist_name, asset_key)

    if len(parts) != 1:
        return None, None, None

    asset_key = parts[0]
    if not is_valid_layout_asset_key(asset_key):
        return None, None, None
    return asset_key, None, None


def _available_layout_asset_sources() -> list[str]:
    sources = []
    if not ARTIST_DIR.exists():
        return sources
    for artist_dir in sorted([path for path in ARTIST_DIR.iterdir() if path.is_dir()], key=lambda path: path.name.lower()):
        for asset_dir in sorted([path for path in artist_dir.iterdir() if path.is_dir()], key=lambda path: path.name.lower()):
            if (asset_dir / "front.png").exists() and (asset_dir / "back.png").exists():
                sources.append(f"{artist_dir.name}/{asset_dir.name}")
    return sources


def _load_layout_asset_source(artist_name: str, asset_key: str) -> Optional[PresetLayoutAsset]:
    source_path = ARTIST_DIR / artist_name / asset_key
    front = _open_rgba(source_path / "front.png")
    back = _open_rgba(source_path / "back.png")
    if front is None or back is None:
        return None
    return PresetLayoutAsset(front=front, back=back)


def _layout_asset_text_color(artist_name: str, asset_key: str) -> Optional[str]:
    config_path = ARTIST_DIR / artist_name / "config.json"
    if not config_path.exists():
        return None
    try:
        with config_path.open("r", encoding="utf-8") as file:
            config = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None

    for season in (config.get("seasons") or {}).values():
        if not isinstance(season, dict):
            continue
        for class_name, color_spec in season.items():
            if class_name == "display":
                continue
            if isinstance(color_spec, (list, tuple)) and len(color_spec) >= 2 and str(color_spec[0]) == asset_key:
                return _normalize_color(color_spec[1], "#000000")
    return None


def _is_safe_path_name(value: str) -> bool:
    return bool(value) and value not in {".", ".."} and "/" not in value and "\\" not in value


def _normalize_color(value: Any, default: str) -> str:
    if not value:
        return default
    try:
        return rgba_to_hex(str(value))
    except (TypeError, ValueError):
        return default


def _image_value(value: Any) -> Optional[Image.Image]:
    if value is None:
        return None
    if isinstance(value, Image.Image):
        return value.convert("RGBA").copy()
    path = _path_value(value)
    if not path:
        return None
    with Image.open(path) as image:
        return image.convert("RGBA").copy()


def _open_rgba(path: Path) -> Optional[Image.Image]:
    if not path.exists():
        return None
    with Image.open(path) as image:
        return image.convert("RGBA").copy()


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
