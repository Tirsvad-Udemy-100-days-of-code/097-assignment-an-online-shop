# Headless browser used for the end-to-end tests and the screenshots.
# Build:  docker build -t online-shop-shots tools/screenshots
# Python 3.14, the version the project requires (python:3.14-slim, pinned by digest).
FROM python@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f
# Flask is pinned to the version of pyproject.toml.
RUN pip install --no-cache-dir Flask==3.1.3 playwright==1.56.0 pytest==8.3.4 \
    && playwright install --with-deps chromium
WORKDIR /work
ENV PYTHONPATH=/work/src
# The container is local and short-lived and has no published port. It runs as root
# only to write the PNG into the folder that the host mounts at /work.
# nosemgrep
ENTRYPOINT ["python", "/work/tools/screenshots/capture.py"]
