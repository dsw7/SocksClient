.PHONY = test lint full
.DEFAULT_GOAL = full

PYTHON_INTERP = /usr/bin/env python3
ROOT_DIRECTORY := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
LIGHT_PURPLE = "\033[1;1;35m"
NO_COLOR = "\033[0m"

define ECHO_STEP
	@echo -e $(LIGHT_PURPLE)\> $(1)$(NO_COLOR)
endef

test:
	$(call ECHO_STEP,Running pytest)
	@$(PYTHON_INTERP) -m pytest --verbose --capture=no 

lint:
	$(call ECHO_STEP,Linting project)
	@$(PYTHON_INTERP) -m pylint $(ROOT_DIRECTORY) --exit-zero --rcfile=$(ROOT_DIRECTORY)/.pylintrc

full: test lint
