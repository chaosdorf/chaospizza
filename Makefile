.PHONY: all
all: run

.PHONY: venv
venv:
	pyenv virtualenv 3.6.1 chaospizza-3.6.1

.PHONY: install-dev
install-dev:
	pip install -r requirements/dev.txt

.PHONY: install-prod
install-prod:
	pip install -r requirements/prod.txt

.PHONY: requirements
requirements:
	$(MAKE) -C requirements all

.PHONY: check
check:
	@which python > /dev/null
	@which pylint > /dev/null
	@which pycodestyle > /dev/null
	@which pydocstyle > /dev/null
	@which pytest > /dev/null
	@which coveralls > /dev/null

.PHONY: lint
lint: check
	pylint chaospizza/ config/
	pycodestyle chaospizza/ config/
	pydocstyle chaospizza/ config/

staticfiles:
	python manage.py collectstatic --settings config.settings.test

.PHONY: test
test: lint staticfiles
	pytest --pythonwarnings=all --cov=chaospizza --cov-report html

.PHONY: only
testonly:
	pytest --pythonwarnings=all $(TESTOPTS)

.PHONY: repl-test
repl-test:
	python manage.py shell --settings config.settings.test

.PHONY: migrate
migrate: test
	python manage.py migrate

.PHONY: run
run: migrate
	python manage.py runserver

.PHONY: repl-dev
repl-dev:
	python manage.py shell

.PHONY: clean
clean:
	-find . -name '__pycache__' -exec rm -r "{}" \; 2>/dev/null
	-rm -rf staticfiles/
	-rm -f .coverage
	-rm -rf coverage_report/
