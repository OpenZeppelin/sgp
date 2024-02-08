#!/bin/bash

source ./bin/activate
pip install ruff

ruff check .
ruff format .
