# FastAPI backend app
Приложение для бэкенда личных проектов

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Code style: Black](https://img.shields.io/badge/Code%20style-Black-000000?style=for-the-badge&logo=python&logoColor=white)](https://github.com/psf/black)
[![Lint: Ruff](https://img.shields.io/badge/Lint-Ruff-2b9348?style=for-the-badge&logo=python&logoColor=white)](https://github.com/astral-sh/ruff-action)
[![Type checking: mypy](https://img.shields.io/badge/Type%20checking-mypy-007ec6?style=for-the-badge&logo=python&logoColor=white)](https://github.com/python/mypy)
[![Dependencies: Poetry](https://img.shields.io/badge/dependencies-Poetry-8A2BE2?style=for-the-badge&logo=python&logoColor=white)](https://github.com/python-poetry/poetry)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-555555?style=for-the-badge&logo=python&logoColor=white)](https://github.com/pre-commit/pre-commit)


---
## Запуск с помощью systemctl
1. Создать файл сервиса:
```bash
sudo cp api-app.template.service /etc/systemd/system/api-app.service
```
2. Отредактировать файл сервиса, подставив свои значения
   * Указать `User`, `Group`, `WorkingDirectory`
   * Найти строку `ExecStart=` и заменить путь к Python на свой

Получить путь к интерпретатору Poetry
```bash
poetry run which python
```

Затем заменить строку `ExecStart=` примерно на:
```bash
ExecStart=/home/LINUX_USER/.cache/pypoetry/virtualenvs/PROJECT_ENV_NAME_FROM_POETRY/bin/python app/run.py
```
3. Применить изменения и запустить сервис
```bash
sudo systemctl daemon-reload
sudo systemctl enable api-app.service
sudo systemctl start api-app.service
```
4. Проверить статус
```bash
sudo systemctl status api-app.service
```
5. Посмотреть логи
```bash
sudo journalctl -u api-app -f
```
