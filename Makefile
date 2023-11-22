default: test

test: test_only pylint

test_only: env
	.env/bin/py.test -x tests

env: .env/.up-to-date


.env/.up-to-date: setup.py Makefile requirements.txt setup.cfg
    python3 -m virtualenv .env
	.env/bin/python -m pip install -U pip virtualenv
	.env/bin/python -m pip install -e '.[testing,doc]'
	touch $@

pylint: env
	.env/bin/pylint --rcfile=.pylintrc cob

doc: env
	.env/bin/sphinx-build -a -W -E doc build/sphinx/html
