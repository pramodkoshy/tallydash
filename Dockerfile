FROM python:3.9-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"

# Copy application code
COPY . .

# Install the package in development mode
RUN pip install -e .

# Set up Jupyter Lab
RUN jupyter lab --generate-config
COPY jupyter_lab_config.py /root/.jupyter/jupyter_lab_config.py

# Expose Jupyter port
EXPOSE 8888

# Set environment variables
ENV PYTHONPATH=/workspace/src:$PYTHONPATH
ENV JUPYTER_ENABLE_LAB=yes

# Default command
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]