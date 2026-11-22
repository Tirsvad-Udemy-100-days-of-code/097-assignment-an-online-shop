# Headless browser used for the end-to-end tests and the screenshots.
# Build:  docker build -t online-shop-shots tools/screenshots
FROM python@sha256:a1165e272e578941b84abc79e4ab38a0305cd12803a5c4247979ac7655f4d641
# Flask is pinned to the version of pyproject.toml.
RUN pip install --no-cache-dir Flask==3.1.3 playwright==1.49.1 pytest==8.3.4 \
    && playwright install --with-deps chromium
WORKDIR /work
ENV PYTHONPATH=/work/src
# The container is local and short-lived and has no published port. It runs as root
# only to write the PNG into the folder that the host mounts at /work.
# nosemgrep
ENTRYPOINT ["python", "/work/tools/screenshots/capture.py"]
