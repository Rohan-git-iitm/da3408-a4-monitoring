# DA3408 A4: Application Monitoring with Prometheus & Grafana

CPU-only image captioning (BLIP-base) in Streamlit, instrumented with prometheus_client,
scraped by Prometheus alongside node_exporter, visualized in Grafana.

## Files
- `app.py`: Streamlit app (Single and Bulk ZIP modes)
- `captioner.py`: BLIP model loading and captioning
- `metrics.py`: Counters, Gauges, Histograms, Summaries, Info (served on :8000)
- `prometheus.yml`: scrape config for the app (:8000), node_exporter (:9100), Prometheus (:9090)
- `grafana_dashboard.json`: Grafana dashboard export
- `ai_disclosure.md`: recorded AI usage

## Run
    uv venv --python 3.11 .venv && source .venv/bin/activate
    uv pip install torch --index-url https://download.pytorch.org/whl/cpu
    uv pip install transformers pillow streamlit prometheus_client psutil
    streamlit run app.py --server.address 0.0.0.0 --server.fileWatcherType none
    ./node_exporter
    ./prometheus --config.file=prometheus.yml
    docker run -d --name grafana --network host grafana/grafana

## AI use
Code and the Grafana dashboard were developed with help from Claude. The PromQL prompt is in prometheus.yml.
