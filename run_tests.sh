#!/bin/bash

rm -rf package
python -m pytest -p no:cacheprovider
