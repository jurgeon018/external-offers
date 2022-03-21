FROM docker-infra.cian.ru/python-web-build:3.10-v1 AS builder
FROM docker-infra.cian.ru/python-web-runtime:3.10-v1

ENV APPLICATION_NAME external-offers
