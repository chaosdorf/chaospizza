help:
	@echo "web-application development environment"
	@echo "--------------------------------------------------------------------------------"
	@echo ""
	@echo "Install pip dependencies:"
	@echo "    make install"
	@echo ""
	@echo "Run development server:"
	@echo "    make run"
	@echo ""
	@echo "Open REPL with Django:"
	@echo "    make repl"
	@echo ""
	@echo "Remove pycache:"
	@echo "    make clean"
	@echo ""

install:
	pip install -r requirements/dev.txt

migrate:
	python ./manage.py migrate

run: migrate
	python ./manage.py runserver

repl:
	python ./manage.py shell

clean:
	-find src -name '__pycache__' -exec rm -r "{}" \; 2>/dev/null

.PHONY: install migrate run repl clean
