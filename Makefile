help:
	@echo "make help  - Show this help"
	@echo "make clean - Delete all untracked/ignored files and directories"
	@echo "make test  - Tests everything"

clean:
	git ls-files --other --directory | xargs rm -rf

delete-bytecode:
	find relief -iname "*.pyc" -delete

test: delete-bytecode
	tox

.PHONY: help clean delete-bytecode test
