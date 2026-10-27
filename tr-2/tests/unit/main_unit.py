"""Script principal para rodar os testes de unidade sequencialmente."""

import unittest
from tests.unit.event_output_test import run_output
from tests.unit.event_input_test import run_input
from tests.unit.test_notify_service import NotificationServiceTests
from tests.unit.test_match_service import MatchServiceUnitTests


def main() -> None:
    """Executa os testes manuais e as suítes unitárias do sistema."""
    print(" EXECUÇÃO 1: RODANDO TESTE DE ESCRITA (OUTPUT)")
    run_output()

    print()
    print(" EXECUÇÃO 2: RODANDO TESTE DE LEITURA (INPUT)")
    run_input()

    print()
    print(" EXECUÇÃO 3: RODANDO TESTE UNITÁRIO (MATCH SERVICE)")
    loader = unittest.TestLoader()
    match_suite = loader.loadTestsFromTestCase(MatchServiceUnitTests)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(match_suite)

    print()
    print(" EXECUÇÃO 4: RODANDO TESTE UNITÁRIO (NOTIFY SERVICE)")
    notify_suite = loader.loadTestsFromTestCase(NotificationServiceTests)
    runner.run(notify_suite)

    print()
    print(" PROCESSAMENTO DE STREAMS CONCLUÍDO COM SUCESSO!")


if __name__ == "__main__":
    main()
