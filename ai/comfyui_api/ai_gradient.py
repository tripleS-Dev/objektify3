import json
import socket
import urllib.request
import uuid
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import websocket  # pip install websocket-client
from PIL import Image
from config import comfyui_SERVER as SERVER

CLIENT_ID = str(uuid.uuid4())
WORKFLOW_PATH = Path(__file__).with_name("gradient.json")

TEXT_NODE_ID = "2"
SEED_NODE_ID = "12"
WS_RECV_TIMEOUT_SEC = 120
WS_BINARY_HEADER_BYTES = 8


def _load_workflow() -> Dict[str, Any]:
    return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))


def _find_saveimage_websocket_node(workflow: Dict[str, Any]) -> Optional[str]:
    for node_id, node in workflow.items():
        if node.get("class_type") == "SaveImageWebsocket":
            return str(node_id)
    return None


def _normalize_seed_text(
    seed: Optional[int],
    text: Optional[str],
    *,
    seed_12: Optional[int] = None,
    text_2: Optional[str] = None,
) -> Tuple[int, str]:
    """Normalize arguments.

    This module historically used keyword names like `seed_12` and `text_2`.
    For readability, the preferred names are now `seed` and `text`.
    """

    if seed is None:
        seed = seed_12
    if text is None:
        text = text_2

    if seed is None:
        raise TypeError("Missing required argument: seed (or seed_12)")
    if text is None:
        raise TypeError("Missing required argument: text (or text_2)")

    return int(seed), str(text)


def build_gradient_prompt(
    seed: Optional[int] = None,
    text: Optional[str] = None,
    *,
    seed_12: Optional[int] = None,
    text_2: Optional[str] = None,
) -> Tuple[Dict[str, Any], str]:
    """Build a ComfyUI workflow payload for the gradient workflow.

    Notes:
        - `seed` is injected into node id "12".
        - `text` is injected into node id "2".
        - The function also discovers the first SaveImageWebsocket node to listen to.
    """

    seed, text = _normalize_seed_text(seed, text, seed_12=seed_12, text_2=text_2)

    workflow = _load_workflow()

    workflow[SEED_NODE_ID]["inputs"]["seed"] = int(seed)
    workflow[TEXT_NODE_ID]["inputs"]["text"] = str(text)

    target_node_id = _find_saveimage_websocket_node(workflow)
    if not target_node_id:
        raise RuntimeError("Workflow does not contain SaveImageWebsocket node.")

    return workflow, target_node_id


def queue_gradient_prompt(
    seed: Optional[int] = None,
    text: Optional[str] = None,
    *,
    seed_12: Optional[int] = None,
    text_2: Optional[str] = None,
) -> Tuple[str, str]:
    """POST the workflow to ComfyUI and return (prompt_id, websocket_target_node_id)."""

    prompt, target_node_id = build_gradient_prompt(
        seed=seed,
        text=text,
        seed_12=seed_12,
        text_2=text_2,
    )
    data = json.dumps({"prompt": prompt, "client_id": CLIENT_ID}).encode("utf-8")
    req = urllib.request.Request(
        f"http://{SERVER}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    res = json.loads(urllib.request.urlopen(req).read())
    if "error" in res:
        raise RuntimeError(f"ComfyUI validation error: {res.get('error')}\nnode_errors={res.get('node_errors')}")
    return res["prompt_id"], target_node_id


def run_gradient_ws_image(
    seed: Optional[int] = None,
    text: Optional[str] = None,
    *,
    seed_12: Optional[int] = None,
    text_2: Optional[str] = None,
    ws_timeout_sec: int = WS_RECV_TIMEOUT_SEC,
) -> Image.Image:
    """Run the gradient workflow via ComfyUI websocket and return exactly one image.

    Assumption (per project requirement):
        The workflow outputs exactly 1 image via a SaveImageWebsocket node.

    Raises:
        RuntimeError: If no image is received before the prompt completes or if a timeout occurs.
    """

    seed, text = _normalize_seed_text(seed, text, seed_12=seed_12, text_2=text_2)

    ws = websocket.WebSocket()
    ws.settimeout(int(ws_timeout_sec))
    ws.connect(f"ws://{SERVER}/ws?clientId={CLIENT_ID}")

    prompt_id, target_node_id = queue_gradient_prompt(seed=seed, text=text)

    current_node: Optional[str] = None
    watching_prompt = False
    prompt_finished = False
    image_bytes: Optional[bytes] = None

    try:
        while True:
            try:
                out = ws.recv()
            except socket.timeout as exc:
                raise RuntimeError(
                    f"Timed out waiting for websocket image data ({ws_timeout_sec}s). "
                    f"prompt_id={prompt_id}, target_node={target_node_id}"
                ) from exc

            if isinstance(out, str):
                msg = json.loads(out)
                if msg.get("type") != "executing":
                    continue

                data = msg.get("data", {})
                if data.get("prompt_id") != prompt_id:
                    continue

                watching_prompt = True
                current_node = data.get("node")

                # ComfyUI sends node=None when the prompt is done.
                if current_node is None:
                    prompt_finished = True
                    current_node = None

                if prompt_finished and image_bytes is not None:
                    break

                continue

            # SaveImageWebsocket binary frames include a small header before the PNG bytes.
            if watching_prompt and (current_node == target_node_id or prompt_finished):
                # Keep the first image only (project assumption: exactly one output image).
                if image_bytes is None:
                    image_bytes = out[WS_BINARY_HEADER_BYTES:]

            if prompt_finished and image_bytes is not None:
                break

    finally:
        ws.close()

    if image_bytes is None:
        raise RuntimeError("No websocket image received. Check node id and that SaveImageWebsocket exists/enabled.")

    # Load bytes into a memory-backed Pillow image without touching disk.
    with Image.open(BytesIO(image_bytes)) as img:
        # 1) 1158 x 1673으로 리사이즈
        return img.copy()


def run_gradient_ws_images(
    seed: Optional[int] = None,
    text: Optional[str] = None,
    *,
    seed_12: Optional[int] = None,
    text_2: Optional[str] = None,
    ws_timeout_sec: int = WS_RECV_TIMEOUT_SEC,
) -> list[Image.Image]:
    """Backward-compatible wrapper.

    The project now assumes exactly 1 image output; this returns a 1-length list.
    """

    return [
        run_gradient_ws_image(
            seed=seed,
            text=text,
            seed_12=seed_12,
            text_2=text_2,
            ws_timeout_sec=ws_timeout_sec,
        )
    ]
