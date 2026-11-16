#!/bin/sh
# Download PopQA (Mallen et al., 2023) test split as parquet from Hugging Face.
set -e
mkdir -p "$(dirname "$0")/../data/sources"
curl -sL -o "$(dirname "$0")/../data/sources/popqa_test.parquet" \
  "https://huggingface.co/datasets/akariasai/PopQA/resolve/refs%2Fconvert%2Fparquet/default/test/0000.parquet"
