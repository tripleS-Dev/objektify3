from typing import Dict, Any, List
from PIL import Image
from argon2 import PasswordHasher
import pathlib
import json
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def submit(
        creator_name: str,
        password: str,
        discord_id: str | None,
        email_id: str | None,
        color_json: Dict[str, Any],
        default_color_side: str,
        default_color_text: str,
        default_img: Image.Image | None,
        top_logo_save: Image.Image | None,
        qr_logo_save: Image.Image | None,
        side_logo_save: Image.Image | None,
        sign_save: List[Image.Image | None]

    ):
    color_json['creator_name'] = creator_name
    color_json['password'] = ph.hash(password)

    color_json['contact'] = {}
    color_json['contact']['discord'] = discord_id
    color_json['contact']['email'] = email_id

    color_json['default_color'] = []
    color_json['default_color'].append(default_color_side if default_color_side else "#FFFFFF")
    color_json['default_color'].append(default_color_text if default_color_text else "#000000")

    color_json['default'] = True if default_img else False

    color_json['top_logo'] = True if top_logo_save else False
    color_json['qr_logo'] = True if qr_logo_save else False
    color_json['side_logo'] = True if side_logo_save else False

    if not sign_save == None:
        pass

    # 프로젝트 루트 기준 폴더 생성 및 중복 확인
    project_root = pathlib.Path(__file__).resolve().parent.parent.parent
    #print(project_root)
    folder_name = f"{color_json.get('name')}-{creator_name}"
    target_path = project_root / "artists" / folder_name

    if top_logo_save:
        top_logo_save.convert('RGBA').save(target_path / "top_logo.png")

    if target_path.is_dir():
        config_path = target_path / "config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                saved_config = json.load(f)
            saved_creator_name = saved_config.get("creator_name")
            saved_password_hash = saved_config.get("password")
            if saved_creator_name == creator_name:
                try:
                    ph.verify(saved_password_hash, password)
                    # 비밀번호가 일치할 경우 기존 폴더 삭제 후 재생성
                    print("비밀번호 일치")
                    if target_path.exists():
                        import shutil
                        shutil.rmtree(target_path)
                        print("기존 폴더 삭제 완료")
                except VerifyMismatchError:
                    print("비밀번호 불일치")
                    return

            else:
                print('creator_name 불일치')
                return

    target_path.mkdir(parents=True)

    # config.json에 color_json 저장
    with open(target_path / "config.json", "w", encoding="utf-8") as f:
        json.dump(color_json, f, ensure_ascii=False, indent=4)

    # 로고 이미지 저장 (None이 아닌 경우만)
    if top_logo_save:
        top_logo_save.convert('RGBA').save(target_path / "top_logo.png")
    if qr_logo_save:
        qr_logo_save.convert('RGBA').save(target_path / "qr_logo.png")
    if side_logo_save:
        side_logo_save.convert('RGBA').save(target_path / "side_logo.png")

    if default_img:
        default_img.convert('RGBA').save(target_path / "default.png")

    # members 및 sign_save 개수 검증 및 저장
    member_keys = list(color_json['members'].keys())
    if len(member_keys) != len(sign_save):
        raise ValueError(f"color_json['members']의 키 개수({len(member_keys)})와 sign_save의 개수({len(sign_save)})가 일치하지 않습니다.")

    signs_dir = target_path / "signs"
    signs_dir.mkdir(exist_ok=True)

    for idx, key in enumerate(member_keys):
        pil_obj = sign_save[idx][0]
        if pil_obj is not None:
            pil_obj.convert('RGBA').save(signs_dir / f"{key}.png")

