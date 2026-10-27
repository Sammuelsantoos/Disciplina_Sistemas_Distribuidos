"""Script principal para rodar os testes de integração sequencialmente."""

import sys
import unittest
from tests.integration.test_streams import MatchEventInputStreamTests
from tests.integration.test_services import MatchServiceTests
from tests.integration.test_admin_client import AdminClientTests
from tests.integration.test_viewer_client import ViewerClientTests


def main() -> None:
    """Carrega as classes de testes e executa a suíte de integração."""
    print("  EXECUÇÃO: INICIANDO OS TESTES DE INTEGRAÇÃO")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(MatchEventInputStreamTests))
    suite.addTests(loader.loadTestsFromTestCase(MatchServiceTests))
    suite.addTests(loader.loadTestsFromTestCase(AdminClientTests))
    suite.addTests(loader.loadTestsFromTestCase(ViewerClientTests))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n==================================================")
    print(f"  Testes executados: {result.testsRun}")
    print(f"  Erros: {len(result.errors)} | Falhas: {len(result.failures)}")

    if result.wasSuccessful():
        print("  TESTES DE INTEGRAÇÃO CONCLUÍDOS COM SUCESSO!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
