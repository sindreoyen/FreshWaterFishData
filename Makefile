venv:
	python3 -m venv .env

requirements:
	pip install -r requirements.txt

waterbodies:
	python3 src/waterbodies.py