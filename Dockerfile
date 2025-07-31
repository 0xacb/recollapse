FROM python:3.13-alpine AS base

FROM base AS build

WORKDIR /build

COPY setup.py README.md requirements.txt ./
COPY src/ ./src/

RUN pip install --prefix /build .

FROM base

COPY --from=build /build /usr/local

ENTRYPOINT ["recollapse"]
