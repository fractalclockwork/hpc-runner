"""REST API base URL for the Streamlit UI (single source of truth)."""

import os

# Override when API is not on localhost (e.g. Docker: http://host.docker.internal:8000)
API_URL = os.environ.get("HPC_API_URL", "http://localhost:8000")
