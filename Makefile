BUILD_NETWORK=chaospizza_default
BUILD_CONTAINER=chaospizza-build
APPLICATION_CONTAINER=chaospizza

.PHONY: venv
venv:
	pipenv install --dev

.PHONY: build-image
build-image:
	docker build -t $(BUILD_CONTAINER) -f Dockerfile.build .

.PHONY: image
image:
	docker build -t $(APPLICATION_CONTAINER) -f Dockerfile .

.PHONY: check
check:
	docker run \
	--rm $(BUILD_CONTAINER) \
	which python pylint pycodestyle pydocstyle pytest >/dev/null 2>&1

.PHONY: lint-pylint
lint-pylint:
	@echo "Running pylint..."
	docker run \
	-v $(PWD)/src:/opt/app:ro \
	-v $(PWD)/pylintrc:/etc/pylintrc:ro \
	--rm $(BUILD_CONTAINER) \
	pylint --rcfile=/etc/pylintrc chaospizza/ config/ util/

.PHONY: lint-pycodestyle
lint-pycodestyle:
	@echo "Running pycodestyle..."
	docker run \
	-v $(PWD)/src:/opt/app:ro \
	-v $(PWD)/setup.cfg:/etc/pycodestyle.cfg:ro \
	--rm $(BUILD_CONTAINER) \
	pycodestyle --config /etc/pycodestyle.cfg chaospizza/ config/ util/

.PHONY: lint-pydocstyle
lint-pydocstyle:
	@echo "Running pydocstyle..."
	docker run \
	-v $(PWD)/src:/opt/app:ro \
	-v $(PWD)/setup.cfg:/etc/pydocstyle.cfg:ro \
	--rm $(BUILD_CONTAINER) \
	pydocstyle --config /etc/pydocstyle.cfg chaospizza/ config/ util/

.PHONY: lint
lint: check lint-pylint lint-pycodestyle lint-pydocstyle

.PHONY: test
test:
	@echo "Running pytest with code coverage..."
	docker run \
	--network $(BUILD_NETWORK) \
	-v $(PWD)/src:/opt/app:ro \
	-v $(PWD)/pytest.ini:/usr/src/pytest.ini:ro \
	-v $(PWD)/coveragerc:/etc/coveragerc:ro \
	-v $(PWD)/build/coverage:/tmp/coverage:rw \
	-e DJANGO_SETTINGS_MODULE=config.settings.test \
	-e DJANGO_DATABASE_URL=$(DJANGO_DATABASE_URL) \
	--rm $(BUILD_CONTAINER) \
	sh -c "python manage.py collectstatic --no-input; pytest --pythonwarnings=all --cov=chaospizza --cov-report=html --cov-config=/etc/coveragerc $(TESTOPTS)"

.PHONY: dev-shell
dev-shell:
	docker run \
	-it \
	--network $(BUILD_NETWORK) \
	-v $(PWD)/src:/opt/app:ro \
	-e DJANGO_SETTINGS_MODULE=config.settings.dev \
	-e DJANGO_DATABASE_URL=$(DJANGO_DATABASE_URL) \
	--rm $(BUILD_CONTAINER) \
	sh

.PHONY: start-db
start-db:
	docker-compose up -d db

.PHONY: migrate
migrate:
	docker run \
	-it \
	--network $(BUILD_NETWORK) \
	-v $(PWD)/src:/opt/app:ro \
	-e DJANGO_SETTINGS_MODULE=config.settings.dev \
	-e DJANGO_DATABASE_URL=$(DJANGO_DATABASE_URL) \
	--rm $(BUILD_CONTAINER) \
	python manage.py migrate

.PHONY: run
run:
	docker-compose up app

.PHONY: stop
stop:
	docker-compose stop

.PHONY: restart
restart: stop start

.PHONY: status
status:
	docker-compose ps

.PHONY: logs
logs:
	docker-compose logs -f

.PHONY: clean
clean: stop
	-docker-compose rm --force
	-rm -rf build/

