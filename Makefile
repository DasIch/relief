help:
	@echo "make help          - Show this help"
	@echo "make dev           - Installs all dependencies and development tools"
	@echo "make clean         - Delete all untracked/ignored files and" \
	                            "directories"
	@echo "make test          - Tests everything"
	@echo "make coverage      - Make coverage report"
	@echo "make view-coverage - View coverage report in a browser"
	@echo "make style         - Run pyflakes on all files"
	@echo "make docs          - Build the documentation"
	@echo "make view-docs     - Show the documentation in a browser"

dev:
	pip install --use-mirrors -r requirements.txt
	pip install -e .

clean:
	git ls-files --other --directory | xargs rm -rf

delete-bytecode:
	find relief -iname "*.pyc" -delete

test: delete-bytecode
	tox

coverage:
	py.test --cov relief

view-coverage: coverage
	coverage html
	open htmlcov/index.html

style:
	find relief -iname "*.py" | xargs pyflakes

docs:
	make -C docs html

view-docs: docs
	open docs/_build/html/index.html

test-docs: docs
	sphinx-build -aEWb doctest -d docs/_build/doctrees docs docs/_build

.PHONY: help dev clean delete-bytecode test coverage view-coverage style \
	docs view-docs test-docs
