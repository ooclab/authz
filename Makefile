default: lint test

lint:
	pylint src tests
	flake8 src tests
	black

test:
	nose2 -v --with-coverage
