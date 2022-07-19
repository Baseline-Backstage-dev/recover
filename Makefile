# ~~~~~~~~~~~~~~~ LOCAL DEVELOPMENT ~~~~~~~~~~~~~~~ #
# This makefile contains all the coommands that are useful for local development

# ~~~~~~~~~~~~~~~ Preamble ~~~~~~~~~~~~~~~ #

.PHONY: help venv install localstack deploy destroy venv install precom_install lint_install lint
.SILENT: ;
.DEFAULT_GOAL := help
SHELL := /bin/bash

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort \
		| awk 'BEGIN {FS = "(: ).*?## "}; {printf "\033[36m%-37s\033[0m %s\n", $$1, $$2}'

# ~~~~~~~~~~~~~~~ Definitions ~~~~~~~~~~~~~~~ #

# Should be defined in specific module
PROJECT_NAME=recover

define VENV
source venv/bin/activate
endef

LOCALSTACK_API_KEY="YtFs2E26Ji"

# ~~~~~~~~~~~~~~~ Commands ~~~~~~~~~~~~~~~ #

venv: ## build a virtual env and install poetry
	test -d venv || python3.9 -m venv venv && venv/bin/pip install --quiet --disable-pip-version-check "poetry>=1.2.0b3"

install: venv ## install dependencies
	$(VENV) && poetry install -vvv

localstack: ## Start the localstack container
	docker-compose -f docker-compose-localstack.yaml up --remove-orphans

localstack-local: ## Start the localstack container
	# TODO: Figure out
	$(VENV) && LAMBDA_EXECUTOR=local DEVELOP=1 DEBUG=1 LOCALSTACK_API_KEY=${LOCALSTACK_API_KEY} DNS_ADDRESS=127.0.0.1 localstack --profile pro start

login:
	$(VENV) && pulumilocal login --local

lambda:
	echo "~~~ Updating the lambda layer..."
	echo "Collecting dependencies..."
	mkdir -p lambda_layer && cd lambda_layer && test -d venv || python3.9 -m venv venv && venv/bin/pip install --quiet --disable-pip-version-check "poetry>=1.2.0b3"
	source lambda_layer/venv/bin/activate && poetry install --only main --no-root
	echo "Building layer zip..."
	cd lambda_layer && rm -rf python && mkdir python && \
	cp -r venv/lib/python3.9/site-packages/* python/ && \
	cp -r ../$(PROJECT_NAME) python/ && \
	zip -rq lambda_layer.zip python

init: login
	echo "~~~ Setting up the pulumi localstack"
	$(VENV) && \
	test -s $${HOME}/.pulumi/passphrase.txt || read -s -p "Enter Password for pulumi: " my_password && \
	echo $${my_password} > $${HOME}/.pulumi/passphrase.txt && \
	export PULUMI_CONFIG_PASSPHRASE_FILE=~/.pulumi/passphrase.txt && \
	pulumilocal stack select --create localstack && pulumilocal stack rm --force --yes && \
	pulumilocal stack select --create localstack && \
	pulumilocal config set $(PROJECT_NAME):stage local && \
	pulumilocal config set aws:region eu-west-1

deploy: lambda init ## Deploy using localstack
	echo "~~~ Deploying resources locally"
	export PULUMI_CONFIG_PASSPHRASE_FILE=~/.pulumi/passphrase.txt && \
	$(VENV) && pulumilocal up --yes

redeploy: lambda
	echo "~~~ Deploying resources locally"
	export PULUMI_CONFIG_PASSPHRASE_FILE=~/.pulumi/passphrase.txt && \
	$(VENV) && pulumilocal up --yes

watch: ## Deploy using localstack
	echo "~~~ Watching resources locally"
	export PULUMI_CONFIG_PASSPHRASE_FILE=~/.pulumi/passphrase.txt && \
	$(VENV) && pulumilocal watch

deploy_watch: deploy watch

destroy: login ## Destroy the localstack resources and stack
	echo "~~~ Destroying resources locally"
	$(VENV) && \
	export PULUMI_CONFIG_PASSPHRASE_FILE=~/.pulumi/passphrase.txt && \
	pulumilocal destroy --yes && \
	pulumilocal stack rm --force --yes

redeploy: destroy deploy

# ~~~~~~~~~~~~~~~ Code hygiene ~~~~~~~~~~~~~~~ #

install_precom: ## install the precommit hooks
	$(VENV) && pre-commit install && pre-commit migrate-config && pre-commit autoupdate

lint: ## check formatting and style with black, isort, flake8, mypy
	$(VENV) && pre-commit run --all-files

test: ## run the tests
	$(VENV) && AWS_DEFAULT_REGION=eu-west-1 pytest tests --verbose
