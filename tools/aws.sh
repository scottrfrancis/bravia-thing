#!/usr/bin/env bash

export AWS_ACCESS_KEY_ID=$(tail -n 1 accessKeys.csv | tr -d "\r" | tr "," "\n" | head -n 1)
export AWS_SECRET_ACCESS_KEY=$(tail -n 1 accessKeys.csv | tr -d "\r" | tr "," "\n" | tail -n 1)
export AWS_DEFAULT_REGION="us-west-2"

set -o errexit
set -o nounset
set -o pipefail

# enable interruption signal handling
trap - INT TERM

docker run --rm \
	-t $(tty &>/dev/null && echo "-i") \
	-e "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" \
	-e "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" \
	-e "AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}" \
	-v "$(pwd):/project" \
	daws \
	"$@"