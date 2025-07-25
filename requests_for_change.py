import re
import concurrent.futures
from utils import Utils
from logging_file import print_log

class RequestsForChange:
    def __init__(self, utils: Utils):
        self.utils = utils
        (
            self.st_api
        ) = self.utils.setup_vars_and_instances()

    def get_accounts_empresas(self):
        print_log(
            message=f"[SYSTEM] Iniciando o Processo de Busca das Contas de Empresas.\n",
            log_type="info"
        )

        accounts_empresas: list = []

        process_result = self.st_api.process_request(
            ok_message="ST: Total de Contas obtidos com sucesso.",
            fail_message="ST: Falha ao obter o Total de Contas.\nSegue abaixo: ERROR_MESSAGE\n",
            status_code=200,
            api_request=self.st_api.get_requests(
                endpoint="accounts?fields=type%2Cname%2ChomeFolder%2Cnotes%2CadditionalAttributes&name=E%2A&offset=0&type=user"
            ),
        )

        total_accounts = process_result.get("resultSet", {}).get("totalCount", 0)
        print_log(f"Total de Contas encontradas: {total_accounts}")

        if not total_accounts:
            print_log(
                message=f"Nenhuma conta foi encontrada.",
                log_type="error")
            return False
        
        offsets = list(range(0, total_accounts, 100))
        all_results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.search_pages, offset) for offset in offsets]
            for future in concurrent.futures.as_completed(futures):
                all_results.extend(future.result())

        # print_log(f"Total de contas brutas retornadas: {len(all_results)}\n")

        pattern = re.compile(r"^E\d+")
        for conta in all_results:
            nome = conta["name"]
            if pattern.match(nome):
                accounts_empresas.append(conta)
        
        tamanho = len(accounts_empresas)
        print_log(f"Quantidade de Contas Empresa - {tamanho}")

        return accounts_empresas
    
    def search_pages(self, offset: int):
        return self.st_api.process_request(
            ok_message=f"ST: Página offset {offset} OK.",
            fail_message=f"ST: Falha na página offset {offset}.",
            status_code=200,
            api_request=self.st_api.get_requests(
                endpoint=f"accounts?fields=type%2Cname%2ChomeFolder%2Cnotes%2CadditionalAttributes&name=E%2A&offset={offset}&type=user"
            ),
        ).get("result", [])
    
    def get_transfer_site(self, account_name):
        print_log(
            message=f"[SYSTEM] Verificando se a Conta '{account_name}' possui Transfer Sites.",
            log_type="info"
        )

        process_result = self.st_api.process_request(
            ok_message=f"ST: Transfer Sites do Account de Empresa '{account_name}' obtidos.",
            fail_message=f"ST: Falha ao obter os Tranfer Sites do Account de Empresa '{account_name}' "
            "Segue abaixo a mensagem de erro: ERROR_MESSAGE\n",
            status_code=200,
            api_request=self.st_api.get_requests(
                endpoint=f"sites?fields=id%2Cname%2Caccount%2CadditionalAttributes&account={account_name}"
            ),
        )

        # print_log(f"Sites do Account Template: \n {process_result}\n")                                                      #TODO Remover depois

        if not process_result.get("result"):
            print_log(
                message=f"O Account '{account_name}' não possui Sites.",
                log_type="warn"
            )
            return []
        
        transfer_sites = {}
    
        for site in process_result.get("result"):
            site_name = site["name"]
            transfer_sites[site_name] = site

        return transfer_sites
    
    def add_email_in_applications(self, account_name, site_and_email):
        print_log(
            message=f"[SYSTEM] Iniciando o Processo de Adição dos Emails nos Applications da Conta '{account_name}'.",
            log_type="info"
        )

        falhas = []

        for site, emails in site_and_email.items():
            application_name = "SH_" + site
            emails = ";".join([e.strip() for e in emails.split(";") if e.strip()])
            print_log(f"\nAdicionando o(s) Email(s) '{emails}' na Conta Empresa '{account_name}'.")

            add_email_process_result = self.st_api.process_request(
                ok_message=f"ST: O(s) Email(s) foi adicionado no Application '{application_name}' com sucesso!",
                fail_message=f"ST: Falha ao adicionar o(s) Email(s) no Application '{application_name}'."
                "\nSegue abaixo a mensagem de erro: \nERROR_MESSAGE",
                status_code=204,
                api_request=self.st_api.patch_requests(
                    endpoint=f"applications/{application_name}",
                    value=emails,
                    attribute="additionalAttributes/userVars.notifyempresa",
                )
            )

            if add_email_process_result is False:
                falhas.append(f"Application: {application_name} | ID Empresa: {account_name} | Emails: {emails}")
                continue

        if falhas:
            print_log(
                message=f"\nFalha ao Adicionar o(s) Email(s) nos seguites Applications: \n - " + "\n - ".join(falhas),
                log_type="error"
            )
            return falhas
            
        return True
    
    def get_subscriptions_ADV_NOTIFY(self):
        print_log(
            message=f"[SYSTEM] Iniciando o Processo de Busca das Subscriptions ADV NOTIFY.\n",
            log_type="info"
        )

        process_result = self.st_api.process_request(
            ok_message=f"ST: Quantidade Total de Subscriptions ADV NOTIFY obtida.",
            fail_message=f"ST: Falha ao obter a Quantidade Total de Subscriptions ADV NOTIFY."
            "\nSegue abaixo a mensagem de erro: \nERROR_MESSAGE\n",
            status_code=200,
            api_request=self.st_api.get_requests(
                endpoint="subscriptions?application=ADV_NOTIFY&fields=id&offset=0"
            ),
        )

        total = process_result.get("resultSet", {}).get("totalCount", 0)
        if total == 0:
            print_log("Nenhuma subscription ADV NOTIFY encontrada.", "warn")
            return False

        print_log(f"Total de subscriptions ADV NOTIFY encontradas: {total}")

        offsets = list(range(0, total, 100))
        all_subscriptions = []

        def fetch_page(offset):
            result = self.st_api.process_request(
                ok_message=f"ST: Página offset {offset} OK.",
                fail_message=f"ST: Falha na página offset {offset}.",
                status_code=200,
                api_request=self.st_api.get_requests(
                    endpoint=f"subscriptions?application=ADV_NOTIFY&fields=type%2Cid%2Caccount%2Cfolder%2Capplication&offset={offset}"
                ),
            ).get("result", [])
            return result
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_page, offset) for offset in offsets]
            for future in concurrent.futures.as_completed(futures):
                try:
                    all_subscriptions.extend(future.result())
                except Exception as e:
                    print_log(f"Erro ao processar página de subscriptions: {e}", "error")

        print_log(f"\nTotal de subscriptions ADV NOTIFY carregadas: {len(all_subscriptions)}\n")

        if not all_subscriptions:
            print_log(
                message=f"\nNenhuma conta possui a Subscription ADV NOTIFY.",
                log_type="warn"
            )
            return False
        
        return all_subscriptions