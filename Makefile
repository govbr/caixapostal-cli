VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
DATA_FOLDER = data
.PHONY: help setup

help:
	@echo ""
	@echo "Configuração do CLI Caixa Postal Gov.br para envio de mensagens"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo " make setup			- Configurar o ambiente de envio de mensagens"
	@echo " make setup-envio 	- Configurar ambiente de envio de mensagens"
	@echo " make enviar			- Enviar mensagens para a caixa postal"
	@echo " make limpar 		- Limpar arquivos de envios e logs"
	@echo " make setup-limpar 	- Remover ambiente virtual e arquivos de configuração"
	@echo ""

setup:
	@command -v python3 >/dev/null 2>&1 || { echo "Python 3 não está instalado. Por favor, instale Python 3 primeiro."; exit 1; }
	@echo "Criando ambiente virtual..."
	python3 -m venv $(VENV)
	@echo "Instalando dependências..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PYTHON) setup_wizard.py
	@echo "Configuração concluída! Use 'make enviar' para enviar mensagens."

setup-envio:
	$(PYTHON) setup_wizard.py
	@echo "Configuração concluída! Use 'make enviar' para enviar mensagens."

enviar:
	$(PYTHON) sender.py

limpar:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.log" -delete
	find . -type f -name "*.pyc" -delete
	rm -rf $(DATA_FOLDER)/*

limpar-setup: limpar
	rm -rf $(VENV)
