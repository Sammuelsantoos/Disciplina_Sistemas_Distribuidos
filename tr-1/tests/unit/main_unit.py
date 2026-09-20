"""Script principal para rodar os testes de unidade sequencialmente."""

import unittest
from tests.unit.event_output_test import run_output
from tests.unit.event_input_test import run_input
from tests.unit.test_notify_service import NotificationServiceTests


def main() -> None:
    """Executa os testes manuais e a suíte unitária do notify_service."""
    print(" EXECUÇÃO 1: RODANDO TESTE DE ESCRITA (OUTPUT)")
    run_output()

    print()
    print(" EXECUÇÃO 2: RODANDO TESTE DE LEITURA (INPUT)")
    run_input()

    print()
    print(" EXECUÇÃO 3: RODANDO TESTE UNITÁRIO (NOTIFY SERVICE)")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(NotificationServiceTests)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

    print()
    print(" PROCESSAMENTO DE STREAMS CONCLUÍDO COM SUCESSO!")


if __name__ == "__main__":
    main()
