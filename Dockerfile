FROM python:3.9.17-slim-buster
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN apt-get update && apt-get install --no-install-recommends -y curl build-essential
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /code
COPY poetry.lock pyproject.toml /code/
RUN poetry config virtualenvs.create false
RUN poetry install

#
COPY ./watchonceapi /code/watchonceapi

#
RUN pip install uvicorn
CMD ["uvicorn", "watchonceapi.main:app", "--host", "0.0.0.0", "--port", "8000"]
