cd ~/Desktop/AIops/a4-monitoring
cat > ai_disclosure.md << 'EOF'
# AI Disclosure

This assignment was completed with help from Claude (Anthropic), used as a step-by-step guide while I set up and ran everything in an Ubuntu VM (UTM) on my Mac.

## What AI helped draft and debug:
- **Application code:** `captioner.py` (BLIP model loading and captioning), `app.py` (Streamlit app with Single and Bulk ZIP modes) and `metrics.py` (Counters, Gauges, Histograms, Summaries, Info metric and their labels).
- **Prometheus config:** `prometheus.yml` scrape configuration for the app, node_exporter and Prometheus.
- **Grafana dashboard:** `grafana_dashboard.json`, including panel layout, PromQL queries, colorblind-safe palette, axis labels, legends and panel descriptions. The "Model status" panel was added at my request.
- **Guidance and debugging:** setup commands (uv environment, CPU-only PyTorch, Grafana in Docker), and help diagnosing issues such as an unsaved `app.py`, a Streamlit/Firefox process issue and a VM clock offset.

## What I did
- Set up and ran the full stack in my VM: Python environment, Streamlit app, node_exporter, Prometheus and Grafana.
- Tested Single and Bulk modes, including error cases, and verified metrics through `/metrics`, the Prometheus targets page and Grafana.
- Imported, checked and exported the dashboard, and recorded the dashboard and explanation videos.
- Worked through the logic of each metric and PromQL query so I can compute them by hand during evaluation.

## Prompt used for the PromQL queries
> "Build a Grafana dashboard for a Streamlit BLIP captioning app exposing caption_* Counters, Gauges, Histograms and Summaries plus node_exporter metrics, with rows for health, throughput/latency, workload/clients and system resources, following the 7 plotting commandments."

This prompt is also recorded as a comment at the top of `prometheus.yml`.

## AI-generated PromQL queries
| Panel | Query |
|---|---|
| App / Node exporter status | `up{job="caption_app"}`, `up{job="node"}` |
| Model status | `caption_model_info` |
| Images captioned (15 min) | `sum(increase(caption_images_processed_total{status="success"}[15m]))` |
| Error rate (5 min) | `sum(rate(caption_images_processed_total{status="error"}[5m])) / sum(rate(caption_images_processed_total[5m]))` |
| Active requests | `sum(caption_active_requests)` |
| Throughput by mode | `sum by (mode) (rate(caption_images_processed_total{status="success"}[1m]))` |
| Inference latency p50 / p95 | `histogram_quantile(0.95, sum by (le, mode) (rate(caption_inference_seconds_bucket[5m])))` (and 0.50) |
| Average request vs preprocessing time | `sum by (mode) (rate(caption_request_seconds_sum[5m])) / sum by (mode) (rate(caption_request_seconds_count[5m]))` (same for `caption_preprocess_seconds`) |
| Inference latency distribution | `sum by (le) (increase(caption_inference_seconds_bucket[1m]))` |
| Requests by client | `sum by (client_ip, session_id, mode) (increase(caption_requests_total[15m]))` |
| Bulk job progress | `caption_bulk_images_remaining` |
| Errors by type | `sum by (mode, error_type) (increase(caption_errors_total[5m]))` |
| Average image size / caption length | `..._sum` rate divided by `..._count` rate, by mode |
| VM CPU vs throughput | `100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[1m])))`, app CPU normalised by core count, and throughput |
| Memory | `node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes`, `sum(caption_process_memory_bytes)` |
| Disk I/O | `sum(rate(node_disk_read_bytes_total[1m]))`, `sum(rate(node_disk_written_bytes_total[1m]))` |
| Root disk usage | `100 * (1 - node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})` |
| Load average | `node_load1`, `node_load5`, `count(count by (cpu) (node_cpu_seconds_total))` |
| Bulk upload annotation | `sum(increase(caption_requests_total{mode="bulk"}[15s])) > 0` |
EOF