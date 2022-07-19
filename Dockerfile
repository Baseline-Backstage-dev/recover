From pulumi/pulumi:3.36.0

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./pyproject.toml /pyproject.toml
COPY ./poetry.lock ./poetry.lock
RUN python3 -m pip install --upgrade "poetry>=1.2.0b3" && poetry install
