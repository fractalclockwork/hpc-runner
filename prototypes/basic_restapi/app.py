from flask import Flask, jsonify, render_template
import structlog
from hpc_regression.runner import load_config, run_from_config

logger = structlog.get_logger()
app = Flask(__name__)

@app.route("/api/run_tests")
def run_tests_extract_metrics():
    outputs = run_from_config("../hpc-runner/configs/runners.yaml")
    return jsonify(outputs)

# Return the template html
@app.route("/")
def root():
    return render_template("index.html")
