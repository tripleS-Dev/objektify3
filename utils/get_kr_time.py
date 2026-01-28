import pytz
from datetime import datetime

import secrets
import string

ALPHABET = string.ascii_letters + string.digits  # a-zA-Z0-9

def random_id(len = 9) -> str:
    # CSPRNG 기반: 같은 시간에 동시에 호출돼도(실질적으로) 독립 난수로 생성됨
    return ''.join(secrets.choice(ALPHABET) for _ in range(len))

def get_kr_time():
    korea_time_zone = pytz.timezone('Asia/Seoul')
    current_time_in_korea = datetime.now(korea_time_zone)
    return current_time_in_korea.strftime(f"%Y%m%d-{random_id(8)}")

if __name__ == "__main__":
    print(get_kr_time())