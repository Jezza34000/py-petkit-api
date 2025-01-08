import json
import unittest
from pypetkitapi.feeder_container import Feeder
import re


class TestContainers(unittest.TestCase):

    def test_feeder_data_d4sh(self):
        # Load the JSON file
        with open("d3_device_data.json", "r") as file:
            data = json.load(file)

        # Initialize the object with the JSON data
        feeder_data = Feeder(**data["result"])

        # List of fields to ignore
        ignore_fields = ["free_care_info", "relation", "user"]

        # Function to convert CamelCase to snake_case
        def camel_to_snake(name):
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
            return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

        # Counter for the number of keys tested
        self.keys_tested = 0

        # Function to generate dynamic assertions
        def assert_dict(expected, actual, parent_key=""):
            for key, value in expected.items():
                snake_key = camel_to_snake(key)
                full_key = f"{parent_key}.{snake_key}" if parent_key else snake_key
                if snake_key in ignore_fields:
                    continue
                if isinstance(actual, dict):
                    actual_value = actual.get(snake_key)
                else:
                    actual_value = getattr(actual, snake_key)
                if isinstance(value, dict):
                    assert_dict(value, actual_value, full_key)
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            assert_dict(item, actual_value[i], f"{full_key}[{i}]")
                        else:
                            self.assertEqual(
                                actual_value[i], item, f"Mismatch at {full_key}[{i}]"
                            )
                            self.keys_tested += 1
                else:
                    self.assertEqual(actual_value, value, f"Mismatch at {full_key}")
                    self.keys_tested += 1

        # Generate dynamic assertions
        assert_dict(data["result"], feeder_data)

        # Print the number of keys tested
        print(f"Number of values tested OK: {self.keys_tested}")


if __name__ == "__main__":
    unittest.main()
