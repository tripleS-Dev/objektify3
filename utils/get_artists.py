import os
import json


def list_artist_folders(official=True):
    """
    주어진 경로("./artists") 안에 있는 모든 폴더(디렉토리) 중에서,
    각 폴더 내부의 config.json에 {'official': true/false} 값이
    official 파라미터와 일치하는 폴더 이름만 리스트로 반환합니다.

    :param official: True면 config.json의 "official": true인 폴더만,
                     False면 "official": false인 폴더만 반환
    :return: 조건을 만족하는 폴더 이름 리스트
    """
    path = "./artists"
    result = []

    # artists 디렉토리가 없으면 빈 리스트 반환
    if not os.path.isdir(path):
        return result

    # 해당 경로의 모든 항목(파일·폴더) 가져오기
    entries = os.listdir(path)

    for entry in entries:
        folder_path = os.path.join(path, entry)

        # 실제로 폴더인지 확인
        if not os.path.isdir(folder_path):
            continue

        config_path = os.path.join(folder_path, "config.json")
        # config.json 파일이 없으면 건너뜀
        if not os.path.isfile(config_path):
            continue

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (json.JSONDecodeError, OSError):
            # JSON 파싱 에러나 파일 읽기 실패 시 스킵
            continue

        # config.json에 "official" 키가 있고, 값이 공식 여부(official 파라미터)와 일치하면 결과에 추가
        if config.get("official", False) is official:
            result.append(entry)

    return result


if __name__ == "__main__":
    # 예시 사용법
    print("공식 아티스트 폴더 목록:", list_artist_folders(official=True))
    print("비공식 아티스트 폴더 목록:", list_artist_folders(official=False))
