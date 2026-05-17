.PHONY: help init install install-be install-fe status up down \
        run run-api dev-fe build-fe lint lint-be lint-fe test test-be clean clean-be clean-fe

PYTHON   ?= python3
VENV     ?= .venv
NODE_VER ?= 20
PID_DIR  := .logs
CURDIR   := $(shell pwd)

help:
	@echo "Poker-bot - доступные команды:"
	@echo ""
	@echo "  Установка и настройка:"
	@echo "    init             — полная инициализация: системные пакеты, Python, Node.js"
	@echo "    install          — установка Python + Node зависимостей"
	@echo "    install-be       — установить Python-зависимости"
	@echo "    install-fe       — установить Node.js-зависимости"
	@echo ""
	@echo "  Статус:"
	@echo "    status           — показать состояние сервисов (процессы, порты, uptime)"
	@echo "    up               — запустить все сервисы (API + Bot + Frontend)"
	@echo "    down             — остановить все сервисы"
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

# docker-build:
# 	docker compose build
# 
# docker-up:
# 	docker compose up -d
# 
# docker-down:
# 	docker compose down
# 
# docker-logs:
# 	docker compose logs -f

status:
	@echo "╔══════════════════════════════════════════════════════════════════╗"
	@echo "║                    Poker-bot — Статус сервисов                  ║"
	@echo "╚══════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "━━━ Poker Bot (десктоп-интерфейс PyQt6) ━━━"
	@BOT_PID=$$(ps -eo pid,args | grep '[p]ython.*poker\.main' | awk '{print $$1}' | head -1); \
	if [ -n "$$BOT_PID" ]; then \
		echo "  ✓ Запущен  (PID: $$BOT_PID)"; \
		START=$$(ps -o lstart= -p $$BOT_PID 2>/dev/null); \
		[ -n "$$START" ] && echo "    Старт: $$START"; \
		ELAPSED=$$(ps -o etime= -p $$BOT_PID 2>/dev/null | xargs); \
		[ -n "$$ELAPSED" ] && echo "    Uptime: $$ELAPSED"; \
		echo "    Главное окно управления ботом открыто на экране"; \
	else \
		echo "  ✗ Не запущен  — запустите: make run"; \
	fi
	@echo ""
	@echo "━━━ Local REST API (скриншоты для TableMapper) ━━━"
	@API_PID=$$(ps -eo pid,args | grep '[u]vicorn.*poker\.restapi_local' | awk '{print $$1}' | head -1); \
	if [ -n "$$API_PID" ]; then \
		echo "  ✓ Запущен  (PID: $$API_PID)"; \
		START=$$(ps -o lstart= -p $$API_PID 2>/dev/null); \
		[ -n "$$START" ] && echo "    Старт: $$START"; \
		ELAPSED=$$(ps -o etime= -p $$API_PID 2>/dev/null | xargs); \
		[ -n "$$ELAPSED" ] && echo "    Uptime: $$ELAPSED"; \
		echo "    Адрес: http://127.0.0.1:8005"; \
		echo "    Документация: http://127.0.0.1:8005/docs"; \
	else \
		echo "  ✗ Не запущен  — запустите: make run-api"; \
	fi
	@echo ""
	@echo "━━━ Frontend (веб-инструменты) ━━━"
	@FE_PID=$$(ps -eo pid,args | grep '[n]ode.*vite' | awk '{print $$1}' | head -1); \
	if [ -n "$$FE_PID" ]; then \
		echo "  ✓ Запущен  (PID: $$FE_PID)"; \
		START=$$(ps -o lstart= -p $$FE_PID 2>/dev/null); \
		[ -n "$$START" ] && echo "    Старт: $$START"; \
		ELAPSED=$$(ps -o etime= -p $$FE_PID 2>/dev/null | xargs); \
		[ -n "$$ELAPSED" ] && echo "    Uptime: $$ELAPSED"; \
		PORT=$$(ss -tlnp 2>/dev/null | grep "$$FE_PID" | grep -oP ':\K\d+' | head -1); \
		[ -z "$$PORT" ] && PORT=$$(lsof -i -P -n 2>/dev/null | grep "$$FE_PID" | grep LISTEN | grep -oP ':\K\d+' | head -1); \
		if [ -n "$$PORT" ]; then \
			echo "    Адрес: http://localhost:$$PORT"; \
		else \
			echo "    Адрес: http://localhost:5173 (по умолчанию)"; \
		fi; \
		echo "    Доступно: /tablemapper, /strategyanalyzer, /strategyeditor"; \
	else \
		echo "  ✗ Не запущен  — запустите: make dev-fe"; \
	fi
	@echo ""
	@echo "━━━ Порты ━━━"
	@ss -tlnp 2>/dev/null | grep -E ':(8005|5173|3000) ' || echo "  Нет слушающих процессов на портах 8005/5173/3000"
	@echo ""

up:
	@mkdir -p $(PID_DIR)
	@echo "==> Запуск сервисов..."
	@nohup $(VENV)/bin/uvicorn poker.restapi_local:app --host 127.0.0.1 --port 8005 > $(PID_DIR)/api.log 2>&1 & echo "$$!" > $(PID_DIR)/api.pid; sleep 1; \
	if kill -0 $$(cat $(PID_DIR)/api.pid) 2>/dev/null; then \
		echo "  ✓ REST API запущен (PID: $$(cat $(PID_DIR)/api.pid))"; \
	else \
		echo "  ✗ REST API упал при запуске! Лог:"; cat $(PID_DIR)/api.log; exit 1; \
	fi
	@nohup $(VENV)/bin/python -m poker.main > $(PID_DIR)/bot.log 2>&1 & echo "$$!" > $(PID_DIR)/bot.pid; sleep 2; \
	if kill -0 $$(cat $(PID_DIR)/bot.pid) 2>/dev/null; then \
		echo "  ✓ Bot запущен (PID: $$(cat $(PID_DIR)/bot.pid))"; \
	else \
		echo "  ✗ Bot упал при запуске! Лог:"; cat $(PID_DIR)/bot.log; $(MAKE) down; exit 1; \
	fi
	@cd website && nohup npm run dev > $(CURDIR)/$(PID_DIR)/fe.log 2>&1 & echo "$$!" > $(CURDIR)/$(PID_DIR)/fe.pid; sleep 3; \
	if kill -0 $$(cat $(CURDIR)/$(PID_DIR)/fe.pid) 2>/dev/null; then \
		echo "  ✓ Frontend запущен (PID: $$(cat $(CURDIR)/$(PID_DIR)/fe.pid))"; \
	else \
		echo "  ✗ Frontend упал при запуске! Лог:"; cat $(CURDIR)/$(PID_DIR)/fe.log; $(MAKE) down; exit 1; \
	fi
	@$(MAKE) status

down:
	@echo "==> Остановка сервисов..."
	@if [ -f $(PID_DIR)/api.pid ]; then \
		PID=$$(cat $(PID_DIR)/api.pid); \
		if kill -0 $$PID 2>/dev/null; then \
			kill $$PID 2>/dev/null; echo "  ✓ REST API остановлен"; \
		else \
			echo "  — REST API не был запущен"; \
		fi; \
		rm -f $(PID_DIR)/api.pid; \
	else \
		echo "  — REST API не был запущен"; \
	fi
	@if [ -f $(PID_DIR)/bot.pid ]; then \
		PID=$$(cat $(PID_DIR)/bot.pid); \
		if kill -0 $$PID 2>/dev/null; then \
			kill $$PID 2>/dev/null; echo "  ✓ Bot остановлен"; \
		else \
			echo "  — Bot не был запущен"; \
		fi; \
		rm -f $(PID_DIR)/bot.pid; \
	else \
		echo "  — Bot не был запущен"; \
	fi
	@if [ -f $(PID_DIR)/fe.pid ]; then \
		PID=$$(cat $(PID_DIR)/fe.pid); \
		if kill -0 $$PID 2>/dev/null; then \
			for child in $$(pgrep -P $$PID 2>/dev/null); do kill $$child 2>/dev/null; done; \
			kill $$PID 2>/dev/null; echo "  ✓ Frontend остановлен"; \
		else \
			echo "  — Frontend не был запущен"; \
		fi; \
		rm -f $(PID_DIR)/fe.pid; \
	else \
		echo "  — Frontend не был запущен"; \
	fi
	@echo "==> Готово"

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