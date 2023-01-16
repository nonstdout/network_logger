# Network Logger

1. run api with

```sh
poetry run uvicorn main:app --reload
```

Browse docs at "http://127.0.0.1:8000/docs#"

2. run poller with

```sh
python email_poller.py
```

3. run downtime calculator with:

```sh
python calculate_downtime.py
```

4. run tests:

```sh
pytest -vv
```