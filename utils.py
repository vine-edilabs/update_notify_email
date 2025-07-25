import json
from logging_file import print_log
from st_api import SecureTransportAPI

class Utils:
    def __init__(self) -> None:
        self.dados_config_file = self.get_data_from_json_file()

    def setup_vars_and_instances(self) -> tuple:
        print_log(
            message="SYSTEM: Iniciando configuracao de variaveis de ambiente e classes",
            log_type="info",
        )
        st_host, st_user, st_password, st_header = self.get_env_vars()

        st_api = SecureTransportAPI(
            host=st_host,
            user=st_user,
            password=st_password,
            header=st_header,
            dados_config_file=self.dados_config_file
        )

        return st_api

    def get_env_vars(self) -> tuple:
        print_log(
            message="SYSTEM: Obtendo variaveis de ambiente do arquivo de configuração",
            log_type="info",
        )
        st_host: str = self.dados_config_file["MFT"]["Host"]
        st_user: str = self.dados_config_file["MFT"]["User"]
        st_password: str = self.dados_config_file["MFT"]["Password"]
        st_header: dict = self.dados_config_file["MFT"]["Header"]

        return st_host, st_user, st_password, st_header

    def get_data_from_json_file(self) -> dict:
            print_log(
                message="SYSTEM: Lendo arquivo de configuração",
                log_type="info",
            )
            with open("./config.json", encoding="utf-8") as file:
                print_log(
                    message="SYSTEM: Arquivo de configuracao carregado", log_type="info"
                )
                return json.load(file)