# Petkit API Client

---

[![PyPI](https://img.shields.io/pypi/v/pypetkitapi.svg)][pypi_]
[![Python Version](https://img.shields.io/pypi/pyversions/pypetkitapi)][python version] [![Actions status](https://github.com/Jezza34000/py-petkit-api/workflows/CI/badge.svg)](https://github.com/Jezza34000/py-petkit-api/actions)

---

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=bugs)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]
[![mypy](https://img.shields.io/badge/mypy-checked-blue)](https://mypy.readthedocs.io/en/stable/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

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
import aiohttp
from pypetkitapi.client import PetKitClient
from pypetkitapi.command import DeviceCommand, FeederCommand, LBCommand, LBAction, LitterCommand

logging.basicConfig(level=logging.DEBUG)

async def main():
    async with aiohttp.ClientSession() as session:
        client = PetKitClient(
            username="username",  # Your PetKit account username or id
            password="password",  # Your PetKit account password
            region="FR",  # Your region or country code (e.g. FR, US, etc.)
            timezone="Europe/Paris",  # Your timezone
            session=session,
        )

        await client.get_devices_data()

        # Lists all devices and pet from account

        for key, value in client.petkit_entities.items():
            print(f"{key}: {type(value).__name__} - {value.name}")

        # Read devices or pet information
        print(client.petkit_entities[123456789])

        # Send command to the devices
        ### Example 1 : Turn on the indicator light
        ### Device_ID, Command, Payload
        await client.send_api_request(123456789, DeviceCommand.UPDATE_SETTING, {"lightMode": 1})

        ### Example 2 : Feed the pet
        ### Device_ID, Command, Payload
        # simple hopper :
        await client.send_api_request(123456789, FeederCommand.MANUAL_FEED, {"amount": 1})
        # dual hopper :
        await client.send_api_request(123456789, FeederCommand.MANUAL_FEED, {"amount1": 2})
        # or
        await client.send_api_request(123456789, FeederCommand.MANUAL_FEED, {"amount2": 2})

        ### Example 3 : Start the cleaning process
        ### Device_ID, Command, Payload
        await client.send_api_request(123456789, LitterCommand.CONTROL_DEVICE, {LBAction.START: LBCommand.CLEANING})


if __name__ == "__main__":
    asyncio.run(main())
```

## More example usage

Check at the usage in the Home Assistant integration : [here](https://github.com/Jezza34000/homeassistant_petkit)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
