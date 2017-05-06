.PHONY: minimal
minimal: venv

.PHONY: venv
venv:
	tox -e venv

.PHONY: release
release: venv
	venv/bin/python setup.py sdist bdist_wheel
	venv/bin/twine upload --skip-existing dist/*

.PHONY: test
test:
	tox

.PHONY: clean
clean:
	find -name '*.pyc' -delete
	find -name '__pycache__' -delete
	rm -rf .tox
	rm -rf venv
	rm -rf .venv.touch
	rm -rf .venv.tox.touch
