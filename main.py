from logging_file import startLogger, logger
from utils import Utils
from change_emails import ChangeEmails
import argparse

@logger
def main(args) -> None:
    change_emails: bool = True if args.change_emails else False
    delete_adv_notify: bool = True if args.delete_adv_notify else False

    utils = Utils()
    initial = ChangeEmails(utils=utils)

    if change_emails and not delete_adv_notify:
        initial.start_change_email()

    if delete_adv_notify and not change_emails:
        initial.delete_subs_ADV_NOTIFY()

if __name__ == "__main__":
    startLogger()
    parser = argparse.ArgumentParser(description="Criação de Notificações para Contas de Empresa")

    parser.add_argument("--change_emails", action="store_true", help="Transfere os Emails da UserVars dos Transfer Sites para os Applications.")
    parser.add_argument("--delete_adv_notify", action="store_true", help="Apaga todas as Subscriptions ADV_NOTIFY.")

    args = parser.parse_args()
    main(args)