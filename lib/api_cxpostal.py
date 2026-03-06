from http.client import responses
from json import JSONDecodeError
import datetime
import requests
import time
import asyncio
import aiohttp
from base64 import b64encode


class ApiCxPostal:
    """
    API CLIENT - Caixa Postal
    doc-cxpostal-orgao: https://api-orgaos-cxpostal.estaleiro.serpro.gov.br/swagger/index.html
    doc-cxpostal-gestao: https://gestao-cxpostal.estaleiro.serpro.gov.br/api/swagger/index.html
    doc-cxpostal-cidadao: https://caixapostal.sistema.gov.br/api/swagger/index.html
    doc-notifica: https://meugov.estaleiro.serpro.gov.br/api/swagger-ui.html
    """

    def __init__(self, client_id=None, client_secret=None, api_key=None, env="HOMOLOGACAO"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.basic_auth = b64encode(f"{client_id}:{client_secret}".encode()).decode()
        self.access_token = None
        self.api_key = api_key
        self.expires_in = 0
        self.base_url_push = "http://localhost:8000/"
        self.base_url_gestao = "http://localhost:8000/"
        self.base_url_orgao = "http://localhost:8000/"
        self.endpoint_auth_push = "#"
        self.endpoint_auth_msg = "#"
        self.endpoint_send_push = "#"
        self.endpoint_send_msg = "#"
        self.env = env
        self.set_environment(env)

    def set_environment(self, env):

        """
        Define o ambiente de acesso da API
        :param env:
        :return: None
        """
        match env:
            case "HOMOLOGACAO":
                self.base_url_push = "https://h.meugov.estaleiro.serpro.gov.br"
                self.base_url_gestao = "https://h.gestao-cxpostal.estaleiro.serpro.gov.br"
                self.base_url_orgao = "https://h-api-orgaos-cxpostal.np.estaleiro.serpro.gov.br"
                self.endpoint_auth_push = f"{self.base_url_push}/auth/oauth/token?grant_type=client_credentials"
                self.endpoint_auth_msg = "#"
                self.endpoint_send_push = f"{self.base_url_push}/api/vbeta1/mensagens"
                self.endpoint_send_msg = f"{self.base_url_orgao}/orgao/mensagem/enviar"

            case "PRODUCAO":
                self.base_url_push = "https://meugov.estaleiro.serpro.gov.br"
                self.base_url_gestao = "https://gestao-cxpostal.estaleiro.serpro.gov.br"
                self.base_url_orgao = "https://api-orgaos-cxpostal.estaleiro.serpro.gov.br"
                self.endpoint_auth_push = f"{self.base_url_push}/auth/oauth/token?grant_type=client_credentials"
                self.endpoint_auth_msg = "#"
                self.endpoint_send_push = f"{self.base_url_push}/api/vbeta1/mensagens"
                self.endpoint_send_msg = f"{self.base_url_orgao}/orgao/mensagem/enviar"

        return self

    def get_endpoint(self, msg_type=None, endpoint="AUTH"):
        """
        Retorna o endpoint de API conforme tipo de mensagem e ambiente
        :param msg_type:
        :param endpoint:
        :return:
        """
        match msg_type:
            case 1:
                if endpoint == "AUTH":
                    return self.endpoint_auth_push
                if endpoint == "SEND":
                    return self.endpoint_send_push
                return "#"

            case 2:
                if endpoint == "AUTH":
                    return self.endpoint_auth_msg
                if endpoint == "SEND":
                    return self.endpoint_send_msg
                return "#"
            case _:
                return "#"

    def get_token(self, msg_type=None):
        """
        Retorna o token de acesso da API
        :param msg_type:
        :return:
        """
        if msg_type == 1:
            if self.expires_in > time.time() and self.access_token is not None:
                return self.access_token

            url = self.get_endpoint(msg_type)
            response = requests.post(url=url, headers={
                "Authorization": f"Basic {self.basic_auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            })
            try:
                data = response.json()
            except JSONDecodeError:
                return False

            if response.status_code != 200 or not all(prop in data.keys() for prop in ['expires_in', 'access_token']):
                return False
            self.access_token = data.get('access_token')
            self.expires_in = data.get('expires_in') + time.time()
            return self.access_token

        if msg_type == 2:
            return self.api_key
        return False

    def set_api_key(self, api_key):
        """
        Define a chave de acesso da API
        :param api_key:
        :return:
        """
        self.api_key = api_key
        return self

    def set_template(self, data):
        """
        Cria ou atualiza um template
        :param data:
        :return:
        """
        response = requests.get(
            url=f"{self.base_url_orgao}/api/gestao/templates",
            data=data,
            headers={
                "Authorization": f"Basic {self.api_key}",
                "Content-Type": "application/x-www-form-urlencoded"
            })
        try:
            data = response.json()
        except JSONDecodeError:
            return False
        if response.status_code != 204:
            return False

        return True

    def get_template(self, pagina=1, ativo=True, templates=None):
        """
        Captura uma lista de templates
        :param pagina:
        :param ativo:
        :param templates:
        :return:
        """
        if templates is None:
            templates = []
        response = requests.get(
            url=f"{self.base_url_orgao}/orgao/templates",
            data={
                "pagina": pagina,
                "ativo": ativo,
            },
            headers={"Authorization": f"Bearer {self.api_key}"})

        try:
            data = response.json()
        except JSONDecodeError:
            return templates

        if response.status_code != 200 or not all(prop in data.keys() for prop in ['templates', 'pagina', "total"]):
            return templates

        templates = templates + data.get('templates')

        if len(templates) >= data.get('total'):
            return templates

        return self.get_template(pagina + 1, ativo, templates)

    def get_versao(self, id, pagina=1, templates=None):
        """
        Captura uma lista de versões de um template
        :param id:
        :param pagina:
        :param templates:
        :return:
        """

        if templates is None:
            templates = []

        response = requests.get(
            url=f"{self.base_url_gestao}/gestao/templates/versao",
            data={
                "pagina": pagina,
                "versap": id,
            },
            headers={
                "Authorization": f"Basic {self.api_key}",
                "Content-Type": "application/x-www-form-urlencoded"
            })
        try:
            data = response.json()
        except JSONDecodeError:
            return templates

        if response.status_code != 200 or not all(
                prop in data.keys() for prop in ['templates', 'pagina', "total_registros", "total_paginas"]):
            return templates

        templates = templates + data.get('templates')

        if len(templates) >= data.get('total_registros'):
            return templates

        return self.get_versao(pagina + 1, id, templates)

    def send(self, dataset):
        """
        Realiza o envio assincrono de mensagens via API
        :param dataset:
        :return:
        """
        return asyncio.run(self.send_message(dataset))

    async def send_message(self, dataset):
        tasks = [asyncio.create_task(self.post_message(data)) for data in dataset]
        return await asyncio.gather(*tasks)

    async def post_message(self, data):
        """
        Cria uma requisição POST assincrona para o endpoint de envio de mensagens
        :param data:
        :return:
        """
        default_data = {
            "start": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "end": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": False,
            "message": "",
            "request": data,
            "response_status": "",
            "response_json": "",
            "response_text": "",
        }

        try:
            async with aiohttp.ClientSession() as cs:
                if not self.get_token(data["msg_type"]):
                    default_data["message"] = "Token error"
                    return default_data
                headers = {
                    "Authorization": f"Bearer {self.get_token(data['msg_type'])}",
                    "Content-Type": "application/json"
                }
                url = self.get_endpoint(data["msg_type"], "SEND")

                del data["msg_type"]

                async with cs.post(url=url, json=data, headers=headers) as response:
                    try:
                        default_data["response_status"] = response.status
                        default_data["response_text"] = await response.text()
                        default_data["response_text"] = default_data["response_text"].replace('\r', '').replace('\n', '')
                        default_data["end"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        default_data["status"] = True

                        try:
                            data = await response.json()
                            default_data["response_json"] = data

                        except JSONDecodeError:
                            default_data["message"] = "JSONDecodeError"
                            return default_data

                        return default_data
                    except Exception as e:
                        default_data["message"] = f"{e}"
                        default_data["end"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        return default_data
        except Exception as e:
            default_data["message"] = f"{e}"
            default_data["end"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return default_data

    def get_template_payload_msg(self, msg_type=1):

        if msg_type == 1:
            return {
                "msg_type": msg_type,
                "remetente": {
                    "cnpj": "",
                    "nome": ""
                },
                "titulo": "",
                "conteudo": "",
                "tipo": "D",
                "cpf": ""
            }

        if msg_type == 2:
            return {
                "msg_type": msg_type,
                "template_id": "",
                "has_push": True,
                "versao": "",
                "assunto": "",
                "destinatarios": [],
                "tags": {}
            }
        return False
