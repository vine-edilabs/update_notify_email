import os
import logging
import datetime
import sys
import traceback
import time

def loglevel(level):
    return {
        "NOTSET": 0,
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50
    }.get(level, 20)

def startLogger():
    os.makedirs("./LOGS", exist_ok=True)
    date = datetime.date.today().strftime("%d-%m-%Y")
    logging.basicConfig(
        filename=f"./LOGS/script_update_notify_email_{date}.log",
        format="%(asctime)s:\t%(levelname)s:\t%(message)s",
        level=loglevel("INFO")
    )
    print_log(message=f"""
              ###################################### 
              NOVA EXECUCAO         Data: {date}
              ######################################\n""",
        log_type="info"
    )

def defineLoggingSection(loggingSection: str) -> None:
    print_log(
        message=f"""\n
        #####################################
        INICIANDO - {loggingSection} 
        #####################################\n""",
        log_type="info"
    )

def print_log(message: str, log_type: str = "info"):
    print(message)
    log_method = {
        "warn": logging.warning,
        "error": logging.error,
        "info": logging.info
    }.get(log_type, logging.info)

    log_method(message)

def logger(func):
    def wrapper(*args, **kwargs):
        try:
            print(f"Executing {func.__name__} with args: {args}, kwargs: {kwargs}")
            startTime = time.time()
            result = func(*args, **kwargs)
            endTime = time.time()
            tempoExecucao = endTime - startTime
            if tempoExecucao < 60:
                formatted_time = f"{tempoExecucao:.2f} segundos"
            else:
                minutes = int(tempoExecucao // 60)
                seconds = tempoExecucao % 60
                formatted_time = f"{minutes} minuto(s) e {seconds:.2f} segundos"

            print_log(message=f"{func.__name__} - {formatted_time}")
            return result
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            completeTraceback = traceback.format_exc()
            linhaErro = tb[-1][1]
            print_log(message=
                      f"Um erro ocorreu na função: {func.__name__}, linha: "
                      f"{linhaErro}: {str(e)}. Segue abaixo o Traceback completo:"
                      f"\n\n{completeTraceback}",
                      log_type="error"
            )
            sys.exit()

    return wrapper