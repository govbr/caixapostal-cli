## Manual de Uso - CLI Caixa Postal Gov.br

Esta ferramenta de linha de comando (CLI) permite o envio em lote de mensagens para a Caixa Postal do Gov.br, utilizando arquivos CSV para dados dos cidadãos e JSON para configurações de envio.

## 1. Pré-requisitos

*   **Sistema Operacional:** Linux, macOS e no Windows onde é preciso de WSL Instalado [https://learn.microsoft.com/pt-br/windows/wsl/](https://learn.microsoft.com/pt-br/windows/wsl/)
*   **Linguagem:** Python 3.10 ou superior instalado.
*   **make** e **pyenv** instalados.
*   **Acesso:** Chave de API (`api_key`) e Templates aprovados no Gov.br.




## 2. Preparando os Arquivos de Envio

O sistema funciona lendo pares de arquivos dentro da pasta `data/`. Para cada envio, você precisa de um arquivo **.csv** (dados) e um arquivo **.json** (configuração) com o nome correspondente, isso pode ser gerado com o assistente de configuração.

### 2.1. O Arquivo de Dados (.csv)

Crie um arquivo `nomedoenvio.csv`.
*   **Obrigatório:** Deve conter uma coluna chamada `cpf`.
*   **Opcional:** Outras colunas que servirão como variáveis (tags) para o template da mensagem.
*   **Formatação:** O sistema remove automaticamente pontuação (pontos e traços) dos CPFs e garante 11 dígitos.

**Exemplo (`data/aviso_vacinacao.csv`):**
```csv
cpf,nome,data_agendamento,local
123.456.789-00,João Silva,25/10/2023,Posto Central
98765432100,Maria Oliveira,26/10/2023,Posto Sul
```

## 3. Instalação e Configuração (Wizard)

A ferramenta possui um assistente de configuração automatizado.

1.  Abra o terminal na pasta raiz do projeto.
   
2.  Execute o comando de configuração:

```bash
make setup
```

> **O que isso faz?** Cria uma pasta `venv`, atualiza o `pip` e instala todas as bibliotecas necessárias (Pandas, Requests, Aiohttp, etc.).



### 3.2. Configurações de Arquivo
Tem duas formas de configurar os arquivos 
    1. Usando o comando `make setup` 
    2. Copiando o arquivo `.csv` para a pasta `data`e criando um `.json` para cada envio.

#### 3.2.1. Metodo 1:
O comando ```make setup``` vai perguntar a pasta onde está o arquivo ```.csv```aponte o caminho e responda as perguntas relacionadas ao envio para criação do arquivo de configuração.


#### 3.2.1 Metodo 2:
Crie um arquivo `.json` na pasta `data/` com o **mesmo nome do CSV adicionado de .json**.

Copie seu arquivo `.csv`para a pasta `data/`
> **Atenção:** Se o CSV é `aviso_vacinacao.csv`, o JSON **deve** ser `aviso_vacinacao.csv.json`.

**Estrutura do JSON:**
```json
{
  "api_key": "SUA_CHAVE_DE_API_AQUI",
  "env": "HOMOLOGACAO",
  "assunto": "Aviso de Vacinação",
  "template_id": "ID_DO_TEMPLATE_NO_GOVBR",
  "versao": "1.0",
  "tags": ["nome", "data_agendamento", "local"]
}
```

**Campos:**
*   `env`: Use `"HOMOLOGACAO"` para testes ou `"PRODUCAO"` para envios reais.
*   `tags`: Lista exata dos nomes das colunas do CSV que devem ser enviadas para preencher o template.
*   `template_id`: O ID do modelo cadastrado no sistema do Gov.br.

## 4. Enviando Mensagens

Após colocar os arquivos na pasta `data/`, execute:

```bash
make enviar
```

O sistema irá:
1.  Ler todos os CSVs da pasta `data`.
2.  Validar se existe o JSON de configuração correspondente.
3.  Processar os envios em lotes (padrão de 250.000 destinatários por lote).
4.  Exibir o progresso no terminal.

## 5. Monitoramento e Logs

Durante a execução, o sistema gera logs detalhados na pasta `data/` e exibe um resumo no terminal.

**Exemplo de saída no terminal:**
```text
--------------STATS_CAIXA_POSTAL--------------
SUCESSO:                              1500
FALHA:                                5
  CPF não encontrado:                 3
  Erro de validação:                  2
```

**Arquivos de Log:**
*   `*.out_msg.log`: Contém o detalhe técnico da resposta da API para cada lote enviado.

## 6. Limpeza

Para remover arquivos de log, cache e arquivos temporários gerados após o envio:

```bash
make limpar
```

Para remover tudo, incluindo o ambiente virtual (resetar a instalação):

```bash
make limpar-setup
```

## 7. Resolução de Problemas

*   **Erro "Python 3 não está instalado":** Instale o Python no seu sistema operacional.
*   **O script roda mas não envia nada:** Verifique se o arquivo JSON tem exatamente o nome `nome_do_csv.csv.json`.
*   **Erro de Token/Auth:** Verifique se a `api_key` está correta e se o `env` está apontando para o ambiente correto (HOMOLOGACAO/PRODUCAO).


_____________________________________________________________________



### Sobre a Caixa Postal Gov.br


- A Caixa Postal Gov.br é um domicílio digital do cidação, forte e seguro, autenticado pelo gov.br. 
Nela é possível os órgaõs da Administração enviar comunicação personalizada aos cidadadões.
---

## Fluxo de Comunicação: Do Template ao Cidadão

### 1. Definição e Cadastro (Estratégia)

O órgão da administração pública define a estratégia de comunicação e o conteúdo da mensagem.

* **Criação do Template:** O órgão desenha o modelo da mensagem, que é composto por textos fixos e **variáveis** (ex: `{{nome}}`, `{{protocolo}}`) para personalização.


  **Homologação pelo MGI:** O template deve ser cadastrado previamente na Caixa Postal, garantindo conformidade com a portaria SGD/MGI 4.444/2024.


* **Consulta de Disponibilidade:** O órgão utiliza o endpoint `GET /orgao/templates` para listar e confirmar os modelos ativos e suas respectivas versões.



### 2. Preparação do Envio (Operação)

Com o template aprovado, o órgão prepara os dados dos destinatários.

* **Estrutura da Lista:** Para cada envio, é necessário associar o **CPF** do cidadão às **Tags (variáveis)** que preencherão o template.



### 3. Execução e Agendamento (Distribuição)

O órgão decide como e quando a mensagem deve chegar ao cidadão.

* **Envio Imediato:** Utiliza o `POST /orgao/mensagem/enviar` para disparos diretos e instantâneos.


* **Criação de Eventos:** Para campanhas estruturadas, utiliza-se o `POST /orgao/eventos`, onde é possível agrupar várias listas sob um mesmo nome de evento.


* **Gestão de Tempo:** O endpoint `POST /orgao/eventos/agendar` permite programar o disparo para uma data futura ou reagendar listas existentes. Se a data não for enviada, o sistema assume disparo imediato.


---

Documentação Completa:
[https://api-orgaos-cxpostal.estaleiro.serpro.gov.br/swagger/index.html](https://api-orgaos-cxpostal.estaleiro.serpro.gov.br/swagger/index.html)


