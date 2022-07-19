# ~~~~~~~~~~~~~~~ AWS DEVELOPMENT ~~~~~~~~~~~~~~~ #
# This uses a pulumi container to standardize the configuration, e.g. by storing pulumi states in the same S3 bucket.

# ~~~~~~~~~~~~~~~ Preamble ~~~~~~~~~~~~~~~ #

.PHONY: help init deploy provision destroy removal rmstack check addpylib provision_preview output stack venv install precom_install lint_install lint
.SILENT: ;
.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort \
		| awk 'BEGIN {FS = "(: ).*?## "}; {printf "\033[36m%-37s\033[0m %s\n", $$1, $$2}'

# ~~~~~~~~~~~~~~~ Definitions ~~~~~~~~~~~~~~~ #

# Should be defined in specific module
PROJECT_NAME=recover

# Pattern s3://pulumi-state-manager/<<VENTURE_NAME>>/
PULUMI_STATE_URL:=s3://pulumi-state-manager/example
BRANCH_NAME:=$(shell git branch --show-current)
AWS_PROFILE:=default
ifeq ($(BRANCH_NAME), main)
	STAGE_NAME:=prod
else
	STAGE_NAME:=$(BRANCH_NAME)
endif
PULUMI_STACK_NAME="$(PROJECT_NAME)-$(STAGE_NAME)"

define COMPOSE_FILE_COMMAND
PROJECT_NAME=$(PROJECT_NAME) docker-compose -f docker-compose.yaml
endef
COMPOSE_RUN_COMMAND=$(COMPOSE_FILE_COMMAND) run --name pulumi-local --entrypoint bash --rm

define COMPOSE_PREFIX_CMD
$(COMPOSE_RUN_COMMAND) pulumi -c "pulumi login $(PULUMI_STATE_URL)
endef
COMPOSE_BASE_CMD=$(COMPOSE_PREFIX_CMD) && pulumi stack select $(PULUMI_STACK_NAME)

# ~~~~~~~~~~~~~~~ Commands ~~~~~~~~~~~~~~~ #

deploy: init provision ## Deploy to AWS

init: ## Start pulumi environment
	test -s $${HOME}/.pulumi/passphrase.txt || read -s -p "Enter Password for pulumi: " \
		my_password && echo $${my_password} > $${HOME}/.pulumi/passphrase.txt
	$(COMPOSE_PREFIX_CMD) && pulumi stack select --create $(PULUMI_STACK_NAME) \
		&& pulumi config set $(PROJECT_NAME):stage $(STAGE_NAME) \
		&& pulumi config set aws:region $$(aws configure get region --profile $(AWS_PROFILE))"

provision: ## Provision AWS Infra using Pulumi with -y
	$(COMPOSE_BASE_CMD) && pulumi up"

destroy: destroy-resources rmstack ## Destroy and remove stack with -y

destroy-resources: ## Removing cloud resources
	$(COMPOSE_BASE_CMD) && pulumi destroy -y"

rmstack: ## Remove stack with -y
	$(COMPOSE_BASE_CMD) && pulumi stack rm -y"

check: ## Remove stack with -y
	$(COMPOSE_PREFIX_CMD) && pulumi version && docker version"

build: ## Rebuild the image
	$(COMPOSE_FILE_COMMAND) kill
	$(COMPOSE_FILE_COMMAND) build --no-cache pulumi

preview: init provision_preview ## Pulumi Preview

provision_preview: ## Provision AWS Infra using Pulumi with -y
	$(COMPOSE_BASE_CMD) && pulumi preview"

container: ## Provision AWS Infra using Pulumi with -y
	docker kill pulumi-local-container || true && docker rm pulumi-local-container || true
	$(COMPOSE_FILE_COMMAND) run --entrypoint bash --rm --name pulumi-local-container -d pulumi
	docker exec -it pulumi-local-container \
		bash -c "pulumi login $(PULUMI_STATE_URL) \
		&& pulumi stack select $(PROJECT_NAME)-$(STAGE_NAME) && bash"

output: ## Show pulumi stack output
	$(COMPOSE_BASE_CMD) && pulumi stack output"

stack: ## Show pulumi stack output
	$(COMPOSE_BASE_CMD) && pulumi stack"
