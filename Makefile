VENV = /tmp/.venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
DATA_FOLDER = data

.PHONY: help setup setup-envio enviar limpar limpar-setup

help:
	@echo ""
	@echo "Configuração do CLI Caixa Postal Gov.br para envio de mensagens"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo " make setup          - Configurar o ambiente completo"
	@echo " make setup-envio    - Reconfigurar envio"
	@echo " make enviar         - Enviar mensagens"
	@echo " make limpar         - Limpar arquivos"
	@echo " make limpar-setup   - Reset total"
	@echo ""

setup:
	@command -v python3 >/dev/null 2>&1 || { echo "Python 3 não está instalado."; exit 1; }
	@echo "Criando ambiente virtual..."
	python3 -m venv $(VENV)

	@echo "Validando ambiente..."
	@test -f $(PYTHON) || { echo "Erro ao criar venv"; exit 1; }

	@echo "Instalando dependências..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

	@echo "Executando setup..."
	$(PYTHON) setup_wizard.py

	@echo "Configuração concluída! Use make enviar para enviar mensagens."

setup-envio:
	@echo "Executando setup de envio..."
	$(PYTHON) setup_wizard.py

enviar:
	$(PYTHON) sender.py

limpar:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.log" -delete
	find . -type f -name "*.pyc" -delete
	rm -rf $(DATA_FOLDER)/*

limpar-setup: limpar
	rm -rf $(VENV)