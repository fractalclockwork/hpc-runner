from flask import Flask, jsonify, render_template
import structlog
from pathlib import Path
from hpc_regression.runner import run_from_config


BASE_DIR = Path(__file__).resolve().parents[2]  # prototypes/basic_restapi/

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

logger = structlog.get_logger()

# Build workspace‑absolute config path
CONFIG_PATH = (
    Path(__file__)
    .resolve()
    .parents[3]  # up to DOW-1-26/
    / "hpc-runner"
    / "configs"
    / "runners.yaml"
)

@app.route("/api/run_tests")
def run_tests_extract_metrics():
    outputs = run_from_config(str(CONFIG_PATH))
    return jsonify(outputs)

@app.route("/")
def root():
    return render_template("index.html")

