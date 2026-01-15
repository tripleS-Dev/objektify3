import shutil
from pathlib import Path

def copy_image_to_folder(src_path: str, dest_folder: Path) -> Path:
    """
    src_path: 복사할 원본 이미지 파일 경로
    dest_folder: 이미지가 복사될 대상 폴더 경로 (경로가 없으면 생성)
    returns: 복사된 파일의 전체 경로
    """
    src = Path(src_path)
    if not src.is_file():
        raise FileNotFoundError(f"원본 파일이 존재하지 않습니다: {src}")

    dest_dir = dest_folder
    dest_dir.mkdir(parents=True, exist_ok=True)          # 대상 폴더가 없으면 생성

    dest_path = dest_dir / src.name                      # 같은 파일명으로 복사
    shutil.copy2(src, dest_path)                         # 메타데이터까지 함께 복사