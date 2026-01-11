footer = """
<div
  style="
    position: fixed;
    right: 16px;
    bottom: 14px;
    z-index: 1999; /* 최상단 레벨 */
    text-align: right;
    font: 13px/1.4 system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    color: rgba(255,255,255,0.78);
    pointer-events: none; /* (옵션) 뒤 요소 클릭 방해 방지 */
  "
>
  <div
    style="
      display: inline-block;
      padding: 10px 12px;
      border-radius: 12px;
      background: rgba(0,0,0,0.5);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.25);
      pointer-events: auto; /* (옵션) 링크/버튼만 클릭 가능 */
    "
  >
    <a
      href="https://discord.gg/KAuTCUGXpH"
      target="_blank"
      rel="noopener noreferrer"
      style="
        color: rgba(255, 255, 255, 1); /* 연한 파랑 */
        text-decoration: underline;  /* 밑줄 */
        font-weight: 600;
        cursor: pointer;             /* 마우스 올리면 포인터 */
      "
    >
      Join our Discord
    </a>
    <span style="opacity: 0.75;">for feedback & updates</span>
    <span style="opacity: 0.55;"> · made by</span>
    <span style="opacity: 0.85; font-weight: 600;">hj_sss</span>
  </div>
</div>
"""
