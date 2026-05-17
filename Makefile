.PHONY: help init install install-be install-fe status up down \
        run run-api dev-fe build-fe lint lint-be lint-fe test test-be clean clean-be clean-fe

PYTHON   ?= python3
VENV     ?= .venv
NODE_VER ?= 20

help:
	@echo "Poker-bot - доступные команды:"
	@echo ""
	@echo "  Установка и настройка:"
	@echo "    init             — полная инициализация: системные пакеты, Python, Node.js"
	@echo "    install          — установка Python + Node зависимостей"
	@echo "    install-be       — установить Python-зависимости"
	@echo "    install-fe       — установить Node.js-зависимости"
	@echo ""
	@echo "  Управление сервисами:"
	@echo "    up               — запустить все сервисы (API + Bot + Frontend)"
	@echo "    down             — остановить все сервисы"
	@echo "    status           — показать состояние сервисов"
	@echo ""
	@echo "  Запуск:"
	@echo "    run              — запустить покерный бот (GUI + API)"
	@echo "    run-api          — запустить только REST API (порт 8005)"
	@echo "    dev-fe           — запустить frontend в режиме разработки"
	@echo ""
	@echo "  Сборка:"
	@echo "    build-fe         — собрать frontend для продакшена"
	@echo ""
	@echo "  Тестирование и линтинг:"
	@echo "    test             — запустить все тесты"
	@echo "    test-be          — запустить Python-тесты"
	@echo "    lint             — запустить все линтеры"
	@echo "    lint-be          — запустить pylint"
	@echo "    lint-fe          — запустить eslint для frontend"
	@echo ""
	@echo "  Очистка:"
	@echo "    clean            — полная очистка (backend + frontend)"
	@echo "    clean-be         — удалить venv и __pycache__"
	@echo "    clean-fe         — удалить node_modules и dist"

init: init-system install

init-system:
	@echo "==> Установка системных пакетов..."
	sudo apt update -y
	sudo apt install -y \
		python3 python3-pip python3-venv \
		ffmpeg libsm6 libxext6 \
		tesseract-ocr libtesseract-dev libleptonica-dev \
		'^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev \
		libxrender-dev libxi-dev libxkbcommon-dev \
		libxkbcommon-x11-dev libegl1 curl git
	@echo "==> Установка Node.js $(NODE_VER) (через NodeSource)..."
	@if ! command -v node >/dev/null 2>&1; then \
		curl -fsSL https://deb.nodesource.com/setup_$(NODE_VER).x | sudo -E bash -; \
		sudo apt install -y nodejs; \
	else \
		echo "Node.js уже установлен: $$(node --version)"; \
	fi
	@echo "==> Готово! Системные пакеты установлены."

install: install-be install-fe

install-be:
	@if [ ! -d $(VENV) ]; then $(PYTHON) -m venv $(VENV); fi
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

install-fe:
	@which npm >/dev/null 2>&1 || { echo "Ошибка: npm не найден. Запустите: make init"; exit 1; }
	cd website && npm install --legacy-peer-deps

up:
	@bash scripts/services.sh up

down:
	@bash scripts/services.sh down

status:
	@bash scripts/services.sh status

run:
	$(VENV)/bin/python -m poker.main

run-api:
	$(VENV)/bin/uvicorn poker.restapi_local:app --host 127.0.0.1 --port 8005 --reload

dev-fe:
	cd website && npm run dev

build-fe:
	cd website && npm run build

test: test-be

test-be:
	$(VENV)/bin/pytest -ra -s poker/tests/

lint: lint-be lint-fe

lint-be:
	$(VENV)/bin/pylint poker/

lint-fe:
	cd website && npm run lint

clean: clean-be clean-fe

clean-be:
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	rm -rf .pytest_cache

clean-fe:
	rm -rf website/node_modules website/dist website/.vite