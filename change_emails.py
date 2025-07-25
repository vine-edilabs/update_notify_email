from utils import Utils
from logging_file import print_log
from requests_for_change import RequestsForChange

class ChangeEmails:
    def __init__(self, utils: Utils):
        self.utils = utils
        self.requests_for_change = RequestsForChange(utils=utils)
        (
            self.st_api
        ) = self.utils.setup_vars_and_instances()

    def start_change_email(self):
        print_log(
            message=f"\n\nIniciando o Processo de Mudança dos Emails Notify do Transfer Site para o Application.\n",
            log_type="info"
        )

        accounts_empresa = self.requests_for_change.get_accounts_empresas()

        if not accounts_empresa or accounts_empresa is False:
            print_log(
                message=f"Não é possível prosseguir. Encerrando programa!",
                log_type="error"
            )
            exit(1)

        for idx, account in enumerate(accounts_empresa):
            if account["name"] == "E19849":

                account_name = account["name"]
                empresa_name = account.get("additionalAttributes", {}).get("empresa")

                print_log(
                    message=(
                        "\n\n" + "="*80 +
                        f"\n[SYSTEM] Iniciando Mudança dos Emails de Notificação\n"
                        f"Conta: {account_name} | Empresa: {empresa_name}\n"
                        + "="*80 + "\n\n"
                    ),
                    log_type="info"
                )

                transfer_sites = self.requests_for_change.get_transfer_site(account_name=account_name)
                if not transfer_sites:
                    print_log(
                        message=f"Pulando para a próxima conta...",
                        log_type="warn"
                    )
                    continue

                site_and_email = {}
                for name, site in transfer_sites.items():
                    email_notify = site.get("additionalAttributes", {}).get("userVars.notify")
                    if email_notify:
                        site_and_email[name] = site["additionalAttributes"]["userVars.notify"]
                
                print_log(f"\nSITE E EMAIL - {site_and_email}\n")

                add_email_in_application = self.requests_for_change.add_email_in_applications(
                    account_name=account_name, site_and_email=site_and_email
                )

                sites_not_deletes = []
                falhas = add_email_in_application if isinstance(add_email_in_application, list) else []
                
                for site_name, site_data in transfer_sites.items():
                    site_id = site_data.get("id")
                    email_notify = site_data.get("additionalAttributes", {}).get("userVars.notify")

                    if site_name in [fail.split(" | ")[0].replace("Application: SH_", "") for fail in falhas]:
                        sites_not_deletes.append(site_name)
                        continue

                    print_log(f"\n[SYSTEM] Apagando o Transfer Site '{site_name}'...")
                    process_result = self.st_api.process_request(
                        ok_message=f"ST: Transfer Site Deletado com Sucesso!",
                        fail_message=f"ST: Falha ao Deletar o Transfer Site."
                        "\nSegue abaixo a mensagem de erro: \nERROR_MESSAGE\n",
                        status_code=204,
                        api_request=self.st_api.delete_requests(
                            endpoint=f"sites/{site_id}"
                        ),
                    )

                    if process_result is False:
                        print_log(
                            message=f"[SYSTEM] O Transfer Site não foi Deletado, então ele será mantido na lista de Sites Não Apagados.",
                            log_type="warn"
                        )
                        sites_not_deletes.append(site_name)

                if sites_not_deletes:
                     print_log(
                        message=(
                            "\n[SYSTEM] Os seguintes Transfer Sites NÃO foram apagados:\n - " +
                            "\n - ".join(sites_not_deletes)
                        ),
                        log_type="warn"
                    )
                else:
                    print_log(
                        message="\n[SYSTEM] Todos os Transfer Sites foram apagados com sucesso.",
                        log_type="success"
                    )

        print_log(f"\n\nTodos os Processos foram finalizados. Encerrando o Programa...\n")

    def delete_subs_ADV_NOTIFY(self):
        print_log(
            message=f"\n\nIniciando o Processo de Delete de todas as Subscriptions ADV NOTIFY.\n",
            log_type="info"
        )

        subs_ADV_NOTIFY = self.requests_for_change.get_subscriptions_ADV_NOTIFY()

        if subs_ADV_NOTIFY is False:
            print_log(
                message=f"Não é possível prosseguir. Encerrando programa!\n",
                log_type="error"
            )
            exit(1)

        falhas = []

        for subscription in subs_ADV_NOTIFY:
            print_log(
                message=f"[SYSTEM] Deletando a Subscription '{subscription['folder']}'",
                log_type="warn"
            )

            process_result = self.st_api.process_request(
                ok_message=f"ST: Subscription ADV NOTIFY deletado com Sucesso!",
                fail_message=f"ST: Falha ao Deletar o Subscription ADV NOTIFY."
                "\nSegue abaixo a mensagem de erro: \nERROR_MESSAGE\n",
                status_code=204,
                api_request=self.st_api.delete_requests(
                    endpoint=f"subscriptions/{subscription['id']}"
                ),
            )

            if process_result is False:
                falhas.append(f"Subscription: {subscription['folder']}")
                continue

        if falhas:
            print_log(
                message=f"[SYSTEM] As seguintes Subscriptions não foram deletadas: \n - " + "\n - ".join(falhas),
                log_type="warn"
            )

        print_log(f"\n\nTodos os Processos foram finalizados. Encerrando o Programa...\n")