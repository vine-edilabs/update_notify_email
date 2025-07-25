from logging_file import print_log
from requests import Response
import requests
import urllib3
from typing import Union
import json

# Desabilita avisos de segurança relacionados a requisições HTTPS sem verificação de certificado.
urllib3.disable_warnings()

class SecureTransportAPI:
    def __init__(
        self, host: str, user: str, password: str, header: dict, dados_config_file: dict
    ) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.header = header
        self.dados_config_file = dados_config_file
        self.auth = (self.user, self.password)

    def get_requests(self, endpoint: str) -> Union[dict, bool]:
        response: Response = requests.get(
            f"{self.host}/{endpoint}",
            headers=self.header,
            verify=False,
            auth=self.auth,
        )
        if "General error" in response.text:
            print_log(
                message=f"FALHA CRÍTICA NO ST - Encerrando execução. Segue abaixo mensagem de erro:\n\n{response.text}",
                log_type="error",
            )
            exit(1)
        return response

    def post_requests(
        self,
        payload: dict,
        endpoint: str,
    ) -> None:
        response: Response = requests.post(
            f"{self.host}/{endpoint}",
            json=payload,
            headers=self.header,
            verify=False,
            auth=self.auth,
        )
        if "General error" in response.text:
            print_log(
                message=f"FALHA CRÍTICA NO ST - Encerrando execução. Segue abaixo mensagem de erro:\n\n{response.text}",
                log_type="error",
            )
            exit()
        return response

    def head_requests(self, item_name: str, item_type: str) -> bool:
        response: Response = requests.head(
            f"{self.host}/{item_type}/{item_name}",
            headers=self.header,
            verify=False,
            auth=self.auth,
        )
        return response

    def delete_requests(self, endpoint: str) -> None:
        response: Response = requests.delete(
            f"{self.host}/{endpoint}",
            headers=self.header,
            verify=False,
            auth=self.auth,
        )
        return response

    def patch_requests(self, endpoint: str, value: any, attribute: str) -> None:
        payload: list = [
            {
                "op": "add",
                "path": f"/{attribute}",
                "value": value,
            }
        ]
        response = requests.patch(
            f"{self.host}/{endpoint}",
            headers=self.header,
            verify=False,
            data=json.dumps(payload),
            auth=self.auth,
        )
        return response

    def process_request(
        self, ok_message: str, fail_message: str, status_code: int, api_request
    ):
        if api_request.status_code == status_code:
            print_log(message=ok_message, log_type="info")
            try:
                response_json = api_request.json()
                return response_json if status_code == 200 else None
            except:
                return
        error_message: str = fail_message.replace("ERROR_MESSAGE", api_request.text)
        print_log(message=error_message, log_type="error")
        return False