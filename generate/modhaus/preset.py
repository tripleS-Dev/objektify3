from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from PIL import Image

from config import ARTIST_DIR


ph = PasswordHasher()


@dataclass
class PresetMember:
    name: str
    abbr: Optional[str] = None
    sign: bool = False
    position: Optional[tuple[int, int]] = None
    updated_at: Optional[str] = None

    def to_config(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if self.abbr:
            data["abbr"] = self.abbr
        if self.sign:
            data["sign"] = True
        if self.position:
            data["position"] = [int(self.position[0]), int(self.position[1])]
        return data


@dataclass
class PresetAssets:
    default_img: Optional[Image.Image] = None
    top_logo: Optional[Image.Image] = None
    qr_logo: Optional[Image.Image] = None
    side_logo: Optional[Image.Image] = None
    signs: dict[str, Image.Image] = field(default_factory=dict)

    def clone_image(self, attr: str) -> Optional[Image.Image]:
        image = getattr(self, attr)
        if image is None:
            return None
        return image.convert("RGBA").copy()


@dataclass
class Preset:
    name: str = ""
    official: bool = False
    members: dict[str, PresetMember] = field(default_factory=dict)
    seasons: dict[str, dict[str, Any]] = field(default_factory=dict)
    default_color: list[str] = field(default_factory=lambda: ["#FFFFFF", "#000000"])
    creator_name: str = ""
    password_hash: Optional[str] = None
    contact: dict[str, Optional[str]] = field(default_factory=lambda: {"discord": None, "email": None})
    source_folder: Optional[str] = None
    verified_for_edit: bool = False
    assets: PresetAssets = field(default_factory=PresetAssets)

    @classmethod
    def new(cls) -> Preset:
        return cls()

    @classmethod
    def from_artist_dir(cls, folder: str | Path, artist_dir: Path = ARTIST_DIR) -> Preset:
        folder_name = Path(folder).name
        base_path = artist_dir / folder_name
        config_path = base_path / "config.json"

        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)

        preset = cls(
            name=config.get("name", ""),
            official=bool(config.get("official", False)),
            seasons=config.get("seasons", {}) or {},
            default_color=list(config.get("default_color") or ["#FFFFFF", "#000000"]),
            creator_name=config.get("creator_name", ""),
            password_hash=config.get("password"),
            contact=config.get("contact") or {"discord": None, "email": None},
            source_folder=folder_name,
            verified_for_edit=False,
        )

        for name, info in (config.get("members") or {}).items():
            position = info.get("position")
            preset.members[name] = PresetMember(
                name=name,
                abbr=info.get("abbr"),
                sign=bool(info.get("sign", False)),
                position=tuple(position) if position else None,
                updated_at="loaded" if info.get("sign", False) else None,
            )

        preset.assets.default_img = _open_image(base_path / "default.png") if config.get("default") else None
        preset.assets.top_logo = _open_image(base_path / "top_logo.png") if config.get("top_logo") else None
        preset.assets.qr_logo = _open_image(base_path / "qr_logo.png") if config.get("qr_logo") else None
        preset.assets.side_logo = _open_image(base_path / "side_logo.png") if config.get("side_logo") else None

        signs_dir = base_path / "signs"
        for member_name in preset.members:
            sign = _open_image(signs_dir / f"{member_name}.png")
            if sign is not None:
                preset.assets.signs[member_name] = sign

        return preset

    @property
    def folder_name(self) -> str:
        return f"{_safe_name(self.name)}-{_safe_name(self.creator_name)}"

    @property
    def has_top_logo(self) -> bool:
        return self.assets.top_logo is not None

    @property
    def has_qr_logo(self) -> bool:
        return self.assets.qr_logo is not None

    @property
    def has_side_logo(self) -> bool:
        return self.assets.side_logo is not None

    @property
    def has_default_img(self) -> bool:
        return self.assets.default_img is not None

    def set_members(self, names: list[str] | None) -> None:
        names = [str(name) for name in (names or []) if str(name).strip()]
        valid = set(names)

        for key in list(self.members.keys()):
            if key not in valid:
                del self.members[key]
                self.assets.signs.pop(key, None)

        for name in names:
            if name not in self.members:
                self.members[name] = PresetMember(name=name)

    def set_seasons_from_display(self, displays: list[str] | None) -> None:
        displays = [str(value) for value in (displays or []) if str(value).strip()]
        new_seasons: dict[str, dict[str, Any]] = {}

        for display in displays:
            key = season_display_to_key(display)
            old_data = self.seasons.get(key) or self.seasons.get(display) or {}
            new_data = dict(old_data)
            new_data["display"] = display
            new_seasons[key] = new_data

        self.seasons = new_seasons

    def set_classes(self, season_key: Optional[str], class_names: list[str] | None, default_colors: tuple[str, str]) -> None:
        if not season_key:
            return

        season = self.seasons.setdefault(season_key, {"display": season_key})
        display = season.get("display", season_key)
        class_names = [str(name) for name in (class_names or []) if str(name).strip()]
        valid = set(class_names)

        for key in list(season.keys()):
            if key != "display" and key not in valid:
                del season[key]

        for name in class_names:
            season.setdefault(name, [default_colors[0], default_colors[1]])

        season["display"] = display

    def to_config(self, password_hash: Optional[str] = None) -> dict[str, Any]:
        return {
            "official": bool(self.official),
            "side_logo": self.has_side_logo,
            "top_logo": self.has_top_logo,
            "qr_logo": self.has_qr_logo,
            "default": self.has_default_img,
            "name": self.name,
            "members": {
                name: member.to_config()
                for name, member in self.members.items()
            },
            "seasons": self.seasons,
            "creator_name": self.creator_name,
            "password": password_hash if password_hash is not None else self.password_hash,
            "contact": self.contact,
            "default_color": self.default_color,
        }

    def verify_password(self, password: str) -> bool:
        if self.official or not self.password_hash:
            return False
        try:
            ph.verify(self.password_hash, password)
        except (VerifyMismatchError, VerificationError):
            self.verified_for_edit = False
            return False

        self.verified_for_edit = True
        return True

    def validate_for_save(self, password: str | None, password_confirm: str | None) -> list[str]:
        errors = []
        if not self.name.strip():
            errors.append("Group name is required.")
        if not self.creator_name.strip():
            errors.append("Creator name is required.")
        if not self.members:
            errors.append("At least one member is required.")
        if not self.seasons:
            errors.append("At least one season is required.")
        if not self.all_seasons_have_class():
            errors.append("Every season needs at least one class.")
        if len(self.default_color) != 2 or not all(self.default_color):
            errors.append("Default colors are required.")
        if self.source_folder and not self.verified_for_edit:
            errors.append("Editing this preset requires password verification.")
        if not self.source_folder and not password:
            errors.append("Password is required for a new preset.")
        if password or password_confirm:
            if password != password_confirm:
                errors.append("Password confirmation does not match.")
        return errors

    def all_seasons_have_class(self) -> bool:
        if not self.seasons:
            return False
        for season in self.seasons.values():
            if not any(key != "display" for key in season):
                return False
        return True

    def sign_status_rows(self) -> list[list[Any]]:
        rows = []
        for name, member in self.members.items():
            rows.append(
                [
                    name,
                    "Yes" if member.sign and name in self.assets.signs else "No",
                    list(member.position) if member.position else "",
                    member.updated_at or "",
                ]
            )
        return rows

    def save(
        self,
        password: str | None = None,
        password_confirm: str | None = None,
        artist_dir: Path = ARTIST_DIR,
    ) -> Path:
        errors = self.validate_for_save(password, password_confirm)
        if errors:
            raise ValueError("\n".join(errors))

        password_hash = self.password_hash
        if password:
            password_hash = ph.hash(password)

        target_path = artist_dir / self.folder_name
        source_path = artist_dir / self.source_folder if self.source_folder else None
        same_folder = source_path is not None and target_path.resolve() == source_path.resolve()

        if target_path.exists() and not same_folder:
            raise FileExistsError(f"Preset folder already exists: {target_path.name}")

        tmp_path = artist_dir / f".{target_path.name}.tmp-{int(time.time() * 1000)}"
        if tmp_path.exists():
            shutil.rmtree(tmp_path)
        tmp_path.mkdir(parents=True)

        try:
            self._write_to_path(tmp_path, password_hash)

            if same_folder and target_path.exists():
                shutil.rmtree(target_path)
            tmp_path.rename(target_path)

            if source_path and not same_folder and source_path.exists():
                shutil.rmtree(source_path)
        except Exception:
            if tmp_path.exists():
                shutil.rmtree(tmp_path)
            raise

        self.password_hash = password_hash
        self.source_folder = target_path.name
        self.verified_for_edit = True
        return target_path

    def _write_to_path(self, target_path: Path, password_hash: Optional[str]) -> None:
        with (target_path / "config.json").open("w", encoding="utf-8") as f:
            json.dump(self.to_config(password_hash), f, ensure_ascii=False, indent=4)

        _save_image(self.assets.top_logo, target_path / "top_logo.png")
        _save_image(self.assets.qr_logo, target_path / "qr_logo.png")
        _save_image(self.assets.side_logo, target_path / "side_logo.png")
        _save_image(self.assets.default_img, target_path / "default.png")

        signs_dir = target_path / "signs"
        signs_dir.mkdir(exist_ok=True)
        for member_name, image in self.assets.signs.items():
            _save_image(image, signs_dir / f"{member_name}.png")


def season_display_to_key(season: str) -> str:
    if "/" not in season:
        return season
    left, right = season.rsplit("/", 1)
    return f"{left}{right}"


def _safe_name(value: str) -> str:
    return str(value).strip().replace("/", "").replace("\\", "")


def _open_image(path: Path) -> Optional[Image.Image]:
    if not path.exists():
        return None
    with Image.open(path) as img:
        return img.convert("RGBA").copy()


def _save_image(image: Optional[Image.Image], path: Path) -> None:
    if image is None:
        return
    image.convert("RGBA").save(path)
