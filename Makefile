.PHONY: docs
core:
	rm -fr requests/core
	git clone https://github.com/kennethreitz/requests-core
	cd requests-core && python setup.py compile
	cd .. && mv requests-core/requests_core requests3/core
	rm -fr requests-core
init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock
test:
	# This runs all of the tests, on both Python 2 and Python 3.
	python setup.py test
mypy:
	python setup.py mypy
ci:
	pipenv run py.test -n 8 --boxed --junitxml=report.xml

test-readme:
	@pipenv run python setup.py check --restructuredtext --strict && ([ $$? -eq 0 ] && echo "README.rst and HISTORY.rst ok") || echo "Invalid markup in README.rst or HISTORY.rst!"

flake8:
	pipenv run flake8 --ignore=E501,F401,E128,E402,E731,F821 requests

coverage:
	pipenv run py.test --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=requests tests

publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist .egg requests.egg-info

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"