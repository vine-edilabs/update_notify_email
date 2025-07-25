from logging_file import startLogger, logger, print_log
from utils import Utils
from change_emails import ChangeEmails

@logger
def main() -> None:
    utils = Utils()

    initial = ChangeEmails(utils=utils)
    initial.start_change_email()

if __name__ == "__main__":
    startLogger()
    main()