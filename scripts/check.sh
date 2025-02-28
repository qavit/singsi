#!/bin/bash
export PYTHONPATH=$PWD
black .
isort .
flake8 .
mypy app
