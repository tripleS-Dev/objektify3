import gradio as gr

_EMPTY_SENTINELS = (None, "")

def _is_empty(x) -> bool:
    # None / "" 는 비어있음
    if x in _EMPTY_SENTINELS:
        return True
    # [] 같은 "길이 0" 시퀀스는 비어있음 (단, 문자열은 위에서 처리)
    try:
        return len(x) == 0
    except TypeError:
        # len() 없는 타입은 여기로 (0, False 같은 값은 "비어있음"으로 취급하지 않음)
        return False

def check_blank(*inputs, empty_pred=_is_empty):
    """
    입력들을 가변 인자로 받아서:
      - 모든 입력이 '비어있지' 않으면: primary + interactive=True
      - 하나라도 비어있으면: secondary + interactive=False
    empty_pred를 바꾸면 '비어있음' 정의를 커스터마이즈 가능.
    """
    enabled = all(not empty_pred(v) for v in inputs)
    return gr.Button(
        variant="primary" if enabled else "secondary",
        interactive=enabled
    )