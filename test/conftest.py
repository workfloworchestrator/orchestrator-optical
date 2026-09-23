"""Pytest fixture registration for the execution-test suite.

The fixtures live in the cohesive ``test.support`` modules (database harness,
device stubs, topology seeders); this conftest only re-exports them so pytest
registers them in the ``test/`` scope.
"""

from test.support.db import (  # noqa: F401
    assert_process_completed,
    assert_process_failed,
    clean_database,
    postgres_database,
    product_id_for,
    run_process,
    set_subscription_status,
    subscription_id_of_process,
)
from test.support.devices import (  # noqa: F401
    stub_node_device,
    stub_ods_device,
    stub_pipe_device,
    stub_spectrum_device,
)
from test.support.topology import (  # noqa: F401
    active_coherent_pluggable_host,
    active_location,
    seed_optical_node,
)
