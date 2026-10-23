FROM gitchameleon-agent:sha256-9cec75d648fc0cf6b71267b63a28227f7c21e0c3e15087f612dedf138e3cd72c
ENV VIRTUAL_ENV=/audit/venvs/gcham_venv_547d275af74f
ENV PATH="/audit/venvs/gcham_venv_547d275af74f/bin:$PATH"
COPY task.json /work/task.json
COPY starter.py /work/starter.py
WORKDIR /work
