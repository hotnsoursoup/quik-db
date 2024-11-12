"""Database and test configurations."""

from pyaml_env import parse_config

from tests.utils import update_test_configs


# Load base database configurations
databases = parse_config("./tests/database.yaml")

# Load test configurations from a YAML file
test_configs = parse_config("./tests/tests.yaml")

# Valid tests
valid_test_config = test_configs["valid_tests"]
valid_tests = update_test_configs(valid_test_config, databases)
valid_test_ids = [v["test"] for v in valid_tests]

# Invalid tests
invalid_test_config = test_configs["invalid_tests"]
invalid_tests = update_test_configs(invalid_test_config, databases)
invalid_test_ids = [v["test"] for v in invalid_tests]

# Multi-database tests
valid_multidb_tests = test_configs["multi_db"].get("valid_tests", "")
invalid_multidb_tests = test_configs["multi_db"].get("invalid_tests", "")
