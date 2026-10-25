FROM python:3.13.9-slim-bookworm@sha256:b685a4fa58bb19d1814d78a1ec0f0208f351452724f78b20212c984d6e124a34
COPY wheels /wheels
COPY requirements.lock /requirements.lock
RUN pip install --no-index --find-links=/wheels --require-hashes -r /requirements.lock && rm -rf /wheels
ENV PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
