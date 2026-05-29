# Swordy Skill Manager — Makefile
#
# Usage:
#   make verify       # validate all swordy-* skills
#   make verify NAME=<skill>  # validate a specific skill
#   make test         # run unit tests
#   make all          # verify + test

SHELL := /bin/bash
SKILL_MANAGER := $(shell pwd)
VALIDATOR := $(SKILL_MANAGER)/scripts/verify_all_skills.sh

.PHONY: verify test all

verify:
	@$(VALIDATOR) $(NAME)

test:
	pytest $(SKILL_MANAGER)/scripts/tests/ -v

all: verify test
