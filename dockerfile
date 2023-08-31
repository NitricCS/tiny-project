FROM python:3.11.5-slim-bullseye as compiler
ADD tiny-docker.py .

WORKDIR /app/

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

FROM python:3.11.5-slim-bullseye as runner
WORKDIR /app/
COPY --from=compiler /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
COPY . /app/

ENTRYPOINT [ "python", "./tiny-docker.py" ]