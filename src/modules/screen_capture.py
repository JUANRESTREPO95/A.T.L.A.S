import mss
import mss.tools
from PIL import Image
import io
import base64


def capture_all_monitors():
    with mss.mss() as sct:
        screens = []
        for i, mon in enumerate(sct.monitors):
            if i == 0:
                continue
            screenshot = sct.grab(mon)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            screens.append(img)
        return screens


def capture_primary_monitor():
    with mss.mss() as sct:
        mon = sct.monitors[1]
        screenshot = sct.grab(mon)
        return Image.frombytes("RGB", screenshot.size, screenshot.rgb)


def capture_all_as_one():
    with mss.mss() as sct:
        all_screens = []
        for i, mon in enumerate(sct.monitors):
            if i == 0:
                continue
            screenshot = sct.grab(mon)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            all_screens.append(img)

        if len(all_screens) == 1:
            return all_screens[0]

        total_w = sum(img.width for img in all_screens)
        max_h = max(img.height for img in all_screens)
        canvas = Image.new("RGB", (total_w, max_h))
        x = 0
        for img in all_screens:
            canvas.paste(img, (x, 0))
            x += img.width
        return canvas


def image_to_base64(img, format="PNG"):
    buf = io.BytesIO()
    img.save(buf, format=format)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
