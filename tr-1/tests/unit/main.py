"""Script principal para rodar os testes de streams separados sequencialmente."""

from tests.unit.event_output_test import run_output
from tests.unit.event_input_test import run_input


def main() -> None:
    """Executa o teste de escrita e na sequência o teste de leitura."""
    print(" EXECUÇÃO 1: RODANDO TESTE DE ESCRITA (OUTPUT)")
    run_output()

    print()
    print(" EXECUÇÃO 2: RODANDO TESTE DE LEITURA (INPUT)")
    run_input()

    print()
    print(" PROCESSAMENTO DE STREAMS CONCLUÍDO COM SUCESSO!")


if __name__ == "__main__":
    main()
