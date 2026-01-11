from pathlib import Path
from colorama import init, Fore, Style  # type: ignore
import colorlog  # type: ignore
import argparse
import logging
import pandas as pd  # type: ignore


# ===================== DECORADOR =====================
def decorador(func):
    def wrapper(*args, **kwargs):
        logger.debug(f"ARGS: {args}")
        logger.debug(f"KWARGS: {kwargs}")
        logger.info(f"Iniciando {func.__name__}()")
        resultado = func(*args, **kwargs)
        logger.info(f"Função {func.__name__}() finalizada")
        return resultado
    return wrapper


# ===================== CLASSE =====================
class ListaTarefas:
    """
    Apenas uma classe para criar listas de tarefas
    """
    def __init__(self):
        try:
            self.arquivo_tarefas = Path(__file__).with_name("to_do.csv")

            if not self.arquivo_tarefas.exists():
                self.arquivo_tarefas.touch()

            with open(self.arquivo_tarefas, "r+", encoding="utf-8") as f:
                linhas = f.readlines()
                if not linhas or not linhas[0].startswith("Índice"):
                    f.seek(0)
                    f.write("Índice,Tarefa,Tempo\n")

            logger.info("Arquivo CSV pronto para uso")

        except Exception as e:
            logger.critical(f"Erro ao criar arquivo CSV: {e}")

    # ===================== ADD =====================
    @decorador
    def adicionar_tarefa(self, tarefa: str, tempo: float) -> int:
        """
        Método da lista de tarefas para adicionar uma tarefa
        Se a tarefa for bem sucedida, retorna 0, caso contrário, 1
        """
        try:
            with open(self.arquivo_tarefas, "r", encoding="utf-8") as f:
                indice = len(f.readlines())

            with open(self.arquivo_tarefas, "a", encoding="utf-8") as f:
                print(f"{indice},{tarefa},{tempo}", file=f)

            return 0
        except Exception as e:
            logger.critical(f"Erro ao adicionar tarefa: {e}")
            return 1

    # ===================== REMOVE =====================
    @decorador
    def remover_tarefa(self, indice: int) -> int:
        """
        Método da lista de tarefas para remover uma tarefa com base no índice
        Se a tarefa for bem sucedida, retorna 0, caso contrário, 1
        """
        try:
            with open(self.arquivo_tarefas, "r", encoding="utf-8") as f:
                linhas = f.readlines()

            if indice <= 0 or indice >= len(linhas):
                logger.error("Índice inválido")
                return 1

            linhas.pop(indice)

            with open(self.arquivo_tarefas, "w", encoding="utf-8") as f:
                f.writelines(linhas)

            return 0
        except Exception as e:
            logger.critical(f"Erro ao remover tarefa: {e}")
            return 1

    # ===================== CONTENT =====================
    @decorador
    def ver_tarefas(self) -> int:
        """
        Método da lista de tarefas para listar as tarefas disponíveis
        Se a tarefa for bem sucedida, retorna 0, caso contrário, 1
        """
        try:
            tabela = pd.read_csv(self.arquivo_tarefas)
            if tabela.empty:
                print("Lista vazia.")
                return 0

            tabela.index += 1
            print("-" * 50)
            print(tabela)
            print("-" * 50)
            return 0

        except Exception as e:
            logger.critical(f"Erro ao exibir tarefas: {e}")
            return 1

    # ===================== CLEAR =====================
    @decorador
    def clear_tarefas(self) -> int:
        """
        Método da lista de tarefas para limpar a lista de tarefas
        Se a tarefa for bem sucedida, retorna 0, caso contrário, 1
        """
        try:
            with open(self.arquivo_tarefas, "r", encoding="utf-8") as f:
                linhas = f.readlines()

            if len(linhas) <= 1:
                raise IndexError("Não há tarefas para apagar")

            escolha = input("Tem certeza que deseja apagar tudo? [Y/N]: ").upper()[0]

            if escolha in ["Y", "S"]:
                with open(self.arquivo_tarefas, "w", encoding="utf-8") as f:
                    f.write("Índice,Tarefa,Tempo\n")
                logger.info("Lista limpa com sucesso")
                return 0

            logger.info("Operação cancelada")
            return 1

        except Exception as e:
            logger.critical(f"Erro ao limpar tarefas: {e}")
            return 1


# ===================== MAIN =====================
@decorador
def main(args, logger) -> int:
    try:
        lista: ListaTarefas = ListaTarefas()

        if args.add_option:
            tarefa, tempo = args.add_option
            tempo = float(tempo)

            if len(tarefa) > 30:
                raise ValueError("Tarefa muito longa")

            if tempo >= 1440:
                raise ValueError("Tempo exagerado, vá descansar")
            elif tempo >= 720:
                logger.warning("Mais de 12h de estudo pode ser prejudicial")

            return lista.adicionar_tarefa(tarefa, tempo)

        elif args.remove_option:
            return lista.remover_tarefa(args.remove_option)

        elif args.content_option:
            return lista.ver_tarefas()

        elif args.clear_option:
            return lista.clear_tarefas()

        return 0

    except KeyboardInterrupt:
        logger.warning("Programa interrompido pelo usuário")
        return 1

    except Exception as e:
        logger.critical(f"Erro geral: {e}")
        return 1


# ===================== ENTRADA =====================
if __name__ == "__main__":
    VERSAO = "1.0.1"
    handler = logging.StreamHandler()

    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s[%(asctime)s] - %(levelname)s > "+ Style.BRIGHT + Fore.WHITE +"%(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG": "blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )

    logger = logging.getLogger()
    logger.handlers.clear()  # MUITO IMPORTANTE
    logger.addHandler(handler)
    
    init(autoreset=True)

    parser = argparse.ArgumentParser(
        prog="To-Do List",
        description="Lista de tarefas em Python",
        epilog="Feito por Thiago",
    )
    parser.add_argument(
        "--version",
        help="Exibe a versão atual do programa",
        action="version",
        version=f"%(prog)s {VERSAO}"
    )

    verb = parser.add_mutually_exclusive_group()
    verb.add_argument(
        "-v", "--verbose",
        help="Ativa o modo verboso(Não use com o modo debug)",
        action="store_true"
        )
    verb.add_argument(
        "-d", "--debug",
        help="Ativa o modo debug(Não use com o modo verboso)",
        action="store_true"
        )

    opts = parser.add_mutually_exclusive_group(required=True)
    
    # ADD
    opts.add_argument(
        "--ADD",
        help="Adiciona mais uma tarefa na lista de tarefas",
        dest="add_option",
        nargs=2,
        metavar=("TAREFA", "TEMPO")
        )
    
    # REMOVE
    opts.add_argument(
        "--REMOVE",
        help="Remove um item da lista de tarefas com base no índice",
        dest="remove_option",
        type=int,
        metavar="ÍNDICE"
        )
    
    # CONTENT
    opts.add_argument(
        "--CONTENT",
        help="Mostra todas as tarefas da lista de tarefas",
        dest="content_option",
        action="store_true"
        )
    
    # CLEAR
    opts.add_argument(
        "--CLEAR",
        help="Limpa/Exclui todas as tarefas",
        dest="clear_option",
        action="store_true"
        )

    args = parser.parse_args()
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO if args.verbose else logging.WARNING)

    exit(main(args, logger))
