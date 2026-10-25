import psutil
from prometheus_client import Counter, Gauge, Histogram, Summary, Info, start_http_server

PROC = psutil.Process()

# Counters
IMAGES = Counter("caption_images_processed_total", "Images captioned", ["mode", "status"])
REQUESTS = Counter("caption_requests_total", "Caption requests per client", ["mode", "client_ip", "session_id"])
ERRORS = Counter("caption_errors_total", "Failures by exception type", ["mode", "error_type"])
UPLOAD_BYTES = Counter("caption_upload_bytes_total", "Bytes of image data received", ["mode"])

# Gauges
ACTIVE = Gauge("caption_active_requests", "Requests currently in progress", ["mode"])
BATCH_REMAINING = Gauge("caption_bulk_images_remaining", "Images left in the current ZIP")
MEMORY = Gauge("caption_process_memory_bytes", "Resident memory of the app process (model included)")
MEMORY.set_function(lambda: PROC.memory_info().rss)
CPU = Gauge("caption_process_cpu_percent", "CPU usage of the app process")
CPU.set_function(lambda: PROC.cpu_percent(None))

# Histograms
INFER = Histogram("caption_inference_seconds", "Model inference time per image", ["mode"],
                  buckets=(0.5, 1, 1.5, 2, 3, 5, 8, 13))
IMG_SIZE = Histogram("caption_image_size_bytes", "Uploaded image size", ["mode"],
                     buckets=(5e4, 1e5, 2.5e5, 5e5, 1e6, 2.5e6, 5e6))
CAP_LEN = Histogram("caption_length_words", "Words per generated caption", ["mode"],
                    buckets=(3, 5, 7, 9, 12, 15, 20))
BATCH_TIME = Histogram("caption_bulk_batch_seconds", "Time to caption a whole ZIP",
                       buckets=(5, 10, 30, 60, 120, 300))

# Summaries (expose _count and _sum)
PREPROC = Summary("caption_preprocess_seconds", "Image decode + RGB conversion time", ["mode"])
REQ = Summary("caption_request_seconds", "End-to-end request time", ["mode"])
BATCH_IMAGES = Summary("caption_bulk_batch_images", "Images per uploaded ZIP")

MODEL = Info("caption_model", "Model metadata")


def start(port=8000):
    start_http_server(port)