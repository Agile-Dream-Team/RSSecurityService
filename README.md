
# Middleware Service

This service is intended to expose endpoints to convert http request to kafka distributed events.

Build with:

![Alt text](https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png)

![Alt text](https://github.com/fastapi/fastapi/workflows/Test/badge.svg?event=push&branch=master)

![Alt text](https://coverage-badge.samuelcolvin.workers.dev/fastapi/fastapi.svg)

![Alt text](https://img.shields.io/pypi/v/fastapi?color=%2334D058&label=pypi%20package)

![Alt text](https://img.shields.io/pypi/pyversions/fastapi.svg?color=%2334D058)



## Run Locally

Clone the project

```bash
  git clone git@github.com:fernandogdaza/middlewareService.git
```

Go to the project directory

```bash
  cd middlewareService
```
Create virtual environment
```bash
  python3 -m venv your_venv_name
```
Activate virtual environment
```bash
  source your_venv_name/bin/activate
```
Install dependencies

```bash
  pip install -r /path/to/requirements.txt
```

Modify the .env file with the correct values and run main.py
```bash
  python3 main.py
```

In case you want to run it with Docker, execute
```bash
  docker-compose up -d
```
in the folder root.