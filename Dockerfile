FROM docker-infra.cian.ru/python-web-build:3.8-v1 AS builder
FROM docker-infra.cian.ru/python-web-runtime:3.8-v1

ENV APPLICATION_NAME external-offers
