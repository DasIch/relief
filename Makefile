help:
	@echo "make help      - Show this help"
	@echo "make clean     - Delete all untracked/ignored files and directories"
	@echo "make test      - Tests everything"
	@echo "make style     - Run pyflakes on all files"
	@echo "make docs      - Build the documentation"
	@echo "make view-docs - Show the documentation in a browser"

clean:
	git ls-files --other --directory | xargs rm -rf

delete-bytecode:
	find relief -iname "*.pyc" -delete

test: delete-bytecode style
	tox

style:
	find relief -iname "*.py" | xargs pyflakes

docs:
	make -C docs html

view-docs: docs
	open docs/_build/html/index.html

.PHONY: help clean delete-bytecode test style docs view-docs
