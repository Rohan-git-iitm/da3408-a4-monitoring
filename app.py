import io
import zipfile

import streamlit as st
from PIL import Image
from streamlit.runtime.scriptrunner import get_script_run_ctx

import metrics as m
from captioner import caption, MODEL_ID

IMG_EXT = (".jpg", ".jpeg", ".png")


@st.cache_resource
def boot():
    m.start(8000)
    m.MODEL.info({"model_id": MODEL_ID, "device": "cpu"})
    return True


boot()
ip = st.context.ip_address or "local"
session = get_script_run_ctx().session_id[:8]


def record_error(mode, e):
    m.IMAGES.labels(mode, "error").inc()
    m.ERRORS.labels(mode, type(e).__name__).inc()


def process(data: bytes, mode: str) -> str:
    m.IMG_SIZE.labels(mode).observe(len(data))
    m.UPLOAD_BYTES.labels(mode).inc(len(data))
    with m.PREPROC.labels(mode).time():
        img = Image.open(io.BytesIO(data)).convert("RGB")
    with m.INFER.labels(mode).time():
        text = caption(img)
    m.CAP_LEN.labels(mode).observe(len(text.split()))
    m.IMAGES.labels(mode, "success").inc()
    return text


st.title("CPU Image Captioning")
single, bulk = st.tabs(["Single", "Bulk (ZIP)"])

with single:
    f = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if f and st.button("Caption", key="single_btn"):
        m.REQUESTS.labels("single", ip, session).inc()
        with m.ACTIVE.labels("single").track_inprogress(), m.REQ.labels("single").time():
            try:
                text = process(f.getvalue(), "single")
                st.image(f)
                st.success(text)
            except Exception as e:
                record_error("single", e)
                st.error(f"Could not caption this image: {e}")

with bulk:
    z = st.file_uploader("Upload a ZIP of images", type=["zip"])
    if z and st.button("Caption all", key="bulk_btn"):
        m.REQUESTS.labels("bulk", ip, session).inc()
        with m.ACTIVE.labels("bulk").track_inprogress(), m.REQ.labels("bulk").time(), m.BATCH_TIME.time():
            try:
                with zipfile.ZipFile(z) as zf:
                    names = [n for n in zf.namelist()
                             if n.lower().endswith(IMG_EXT) and not n.startswith("__MACOSX")]
                    m.BATCH_IMAGES.observe(len(names))
                    bar = st.progress(0.0)
                    rows = []
                    for i, name in enumerate(names):
                        m.BATCH_REMAINING.set(len(names) - i)
                        try:
                            rows.append({"file": name, "caption": process(zf.read(name), "bulk")})
                        except Exception as e:
                            record_error("bulk", e)
                            rows.append({"file": name, "caption": f"ERROR: {e}"})
                        bar.progress((i + 1) / len(names))
                    m.BATCH_REMAINING.set(0)
                st.dataframe(rows)
            except zipfile.BadZipFile as e:
                record_error("bulk", e)
                st.error("That file is not a valid ZIP.")