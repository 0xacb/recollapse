FROM python:3.11-alpine as base

FROM base as build

WORKDIR /build

COPY requirements.txt /requirements.txt
RUN pip install --prefix /build -r /requirements.txt

FROM base

COPY --from=build /build /usr/local

WORKDIR /tool

COPY recollapse /tool
RUN chmod +x recollapse

ENTRYPOINT ["/tool/recollapse"]
