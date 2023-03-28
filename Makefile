test:
	python -m pytest -s

lint:
	black premedy && flake8 premedy --ignore=E501,E722,W503
