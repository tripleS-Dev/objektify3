import os
import json
from pathlib import Path
from typing import Any, Dict, Optional


def save_log_json(data: Dict[str, Any], temp_id: str, filename: str = "1.json") -> Path:
    """
    data를 ./logs/{temp_id}/{filename} 에 JSON으로 저장하고,
    저장된 파일 Path를 반환합니다.
    """

    if not temp_id:
        temp_id = 'None'
    log_dir = Path("./logs") / str(temp_id)
    log_dir.mkdir(parents=True, exist_ok=True)

    out_path = log_dir / filename
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")

    # 원자적 저장(중간에 프로그램이 죽어도 파일이 깨질 확률 줄임)
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    os.replace(tmp_path, out_path)  # atomic replace (대부분 OS에서 안전)
    return out_path


# 사용 예시
# path = save_log_json(data, temp_id=temp_id)  # -> ./logs/{temp_id}/1.json 저장
# print("Saved:", path)
