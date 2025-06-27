from datetime import datetime
import pytz

def get_kr_time():
    # 한국 시간대 설정
    korea_time_zone = pytz.timezone('Asia/Seoul')

    # 현재 시간을 한국 시간대로 변환
    current_time_in_korea = datetime.now(korea_time_zone)

    # 원하는 형식으로 시간 포맷팅
    return current_time_in_korea.strftime("%Y%m%d-%H%M%S")