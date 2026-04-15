from pathlib import Path
from integrations.ERM.clients.mock_source_client import MockSourceClient
from integrations.ERM.ports.source import ERMProdOrderSourcePort


def get_erm_source() -> ERMProdOrderSourcePort:
    return MockSourceClient(
        json_path=Path("integrations/ERM/test_data/test_data1.json")
    )
