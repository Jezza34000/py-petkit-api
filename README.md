# Petkit API Client

---

# WIP - UNDER DEVELOPMENT

---

[![PyPI](https://img.shields.io/pypi/v/pypetkitapi.svg)][pypi_]
[![Python Version](https://img.shields.io/pypi/pyversions/pypetkitapi)][python version]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]
[![mypy](https://img.shields.io/badge/mypy-checked-blue)](https://mypy.readthedocs.io/en/stable/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Actions status](https://github.com/Jezza34000/py-petkit-api/workflows/CI/badge.svg)](https://github.com/Jezza34000/py-petkit-api/actions)

---

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)

[pypi_]: https://pypi.org/project/pypetkitapi/
[python version]: https://pypi.org/project/pypetkitapi
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Overview

PetKit Client is a Python library for interacting with the PetKit API. It allows you to manage your PetKit devices, retrieve account data, and control devices through the API.

## Features

Login and session management
Fetch account and device data
Control PetKit devices (Feeder, Litter Box, Water Fountain)

## Installation

Install the library using pip:

```bash
pip install pypetkitapi
```

## Usage Example:

```python
import asyncio
import logging
from pypetkitapi.client import PetKitClient

logging.basicConfig(level=logging.DEBUG)


async def main():
    client = PetKitClient(
        username="username",  # Your PetKit account username
        password="password",  # Your PetKit account password
        region="France",  # Your region
        timezone="Europe/Paris",  # Your timezone
    )

    # To get the account and devices data attached to the account
    await client.get_devices_data()
    # Read the account data
    print(client.account_data)
    # Read the devices data
    print(client.device_list)

    # client.device_list[0] is the first device in the list in this example it's a Feeder
    # Get the Feeder from the device list
    my_feeder = client.device_list[0]

    # Send command to the devices
    ### Example 1 : Turn on the indicator light
    await client.send_api_request(my_feeder, DeviceCommand.UPDATE_SETTING, {"lightMode": 1})

    ### Example 2 : Feed the pet
    await client.send_api_request(my_feeder, FeederCommand.MANUAL_FEED, {"amount": 1})


if __name__ == "__main__":
    asyncio.run(main())
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
