# Petkit API Client

---

[![Lifecycle:Maturing](https://img.shields.io/badge/Lifecycle-Stable-007EC6)](https://github.com/Jezza34000/py-petkit-api/)
[![Python Version](https://img.shields.io/pypi/pyversions/pypetkitapi)][python version] [![Actions status](https://github.com/Jezza34000/py-petkit-api/workflows/CI/badge.svg)](https://github.com/Jezza34000/py-petkit-api/actions)

[![PyPI](https://img.shields.io/pypi/v/pypetkitapi.svg)][pypi_] [![PyPI Downloads](https://static.pepy.tech/badge/pypetkitapi)](https://pepy.tech/projects/pypetkitapi)

---

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api) [![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=bugs)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_py-petkit-api&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=Jezza34000_py-petkit-api)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]
[![mypy](https://img.shields.io/badge/mypy-checked-blue)](https://mypy.readthedocs.io/en/stable/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

[pypi_]: https://pypi.org/project/pypetkitapi/
[python version]: https://pypi.org/project/pypetkitapi
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

### Enjoying this library?

[![Sponsor Jezza34000][github-sponsor-shield]][github-sponsor] [![Static Badge][buymeacoffee-shield]][buymeacoffee]

---

## ℹ️ Overview

PetKit Client is a Python library for interacting with the PetKit API. It allows you to manage your PetKit devices, retrieve account data, and control devices through the API.

## 🚀 Features

- Login and session management
- Fetch account and device data
- Control PetKit devices (Feeder, Litter Box, Water Fountain, Purifiers)
- Fetch images & videos produced by devices
  > Pictures are available **with or without** Care+ subscription, Videos are only available **with** Care+ subscription

## ⬇️ Installation

Install the library using pip:

```bash
pip install pypetkitapi
```

## 💡 Usage Example:

Here is a simple example of how to use the library to interact with the PetKit API \
This example is not an exhaustive list of all the features available in the library.

```python
import asyncio
import logging
import aiohttp
from pypetkitapi.client import PetKitClient
from pypetkitapi.command import DeviceCommand, FeederCommand, LBCommand, DeviceAction, LitterCommand

logging.basicConfig(level=logging.DEBUG)

async def main():
    async with aiohttp.ClientSession() as session:
        client = PetKitClient(
            username="username",  # Your PetKit account username or id
            password="password",  # Your PetKit account password
            region="FR",  # Your region or country code (e.g. FR, US,CN etc.)
            timezone="Europe/Paris",  # Your timezone(e.g. "Asia/Shanghai")
            session=session,
        )

        await client.get_devices_data()

        # Lists all devices and pet from account

        for key, value in client.petkit_entities.items():
            print(f"{key}: {type(value).__name__} - {value.name}")

        # Select a device
        device_id = key
        # Read devices or pet information
        print(client.petkit_entities[device_id])

        # Send command to the devices
        ### Example 1 : Turn on the indicator light
        ### Device_ID, Command, Payload
        await client.send_api_request(device_id, DeviceCommand.UPDATE_SETTING, {"lightMode": 1})

        ### Example 2 : Feed the pet
        ### Device_ID, Command, Payload
        # simple hopper :
        await client.send_api_request(device_id, FeederCommand.MANUAL_FEED, {"amount": 1})
        # dual hopper :
        await client.send_api_request(device_id, FeederCommand.MANUAL_FEED, {"amount1": 2})
        # or
        await client.send_api_request(device_id, FeederCommand.MANUAL_FEED, {"amount2": 2})

        ### Example 3 : Start the cleaning process
        ### Device_ID, Command, Payload
        await client.send_api_request(device_id, LitterCommand.CONTROL_DEVICE, {DeviceAction.START: LBCommand.CLEANING})


if __name__ == "__main__":
    asyncio.run(main())
```

## 💡 More example usage

Check at the usage in the Home Assistant integration : [here](https://github.com/Jezza34000/homeassistant_petkit)

## ☑️ Supported Devices

| **Category**     | **Name**                  | **Device**                                                                                                                                             |
| ---------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **🍗 Feeders**   | ✅ Fresh Element          | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/feeder.png" width="40"/></a>     |
|                  | ✅ Fresh Element Mini Pro | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/feedermini.png" width="40"/></a> |
|                  | ✅ Fresh Element Infinity | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/d3.png" width="40"/></a>         |
|                  | ✅ Fresh Element Solo     | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/d4.png" width="40"/></a>         |
|                  | ✅ Fresh Element Gemini   | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/d4s.png" width="40"/></a>        |
|                  | ✅ YumShare Solo          | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/d4h.png" width="40"/></a>        |
|                  | ✅ YumShare Dual-hopper   | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/d4sh.png" width="40"/></a>       |
| **🚽 Litters**   | ✅ PuraX                  | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/t3.png" width="40"/></a>         |
|                  | ✅ PuraMax                | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/t4.1.png" width="40"/></a>       |
|                  | ✅ PuraMax 2              | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/t4.png" width="40"/></a>         |
|                  | ✅ Purobot Max Pro        | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/t5.png" width="40"/></a>         |
|                  | ✅ Purobot Ultra          | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/t6.png" width="40"/></a>         |
| **⛲ Fountains** | ✅ Eversweet Solo 2       | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/5w5.png" width="40"/></a>        |
|                  | ✅ Eversweet 3 Pro        | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/4w5.png" width="40"/></a>        |
|                  | ✅ Eversweet 3 Pro UVC    | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/6w5.png" width="40"/></a>        |
|                  | ✅ Eversweet 5 Mini       | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/2w5.png" width="40"/></a>        |
|                  | ✅ Eversweet Max          | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/ctw3.png" width="40"/></a>       |
| **🧴 Purifiers** | ✅ Air Magicube           | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/k2.png" width="40"/></a>         |
|                  | ✅ Air Smart Spray        | <a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/devices/k3.png" width="40"/></a>         |

## 🛟 Help and Support

Developers? Want to help? Join us on our Discord channel dedicated to developers and contributors.

[![Discord][discord-shield]][discord]

## 👨‍💻 Contributing

Contributions are welcome!\
Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

[homeassistant_petkit]: https://github.com/Jezza34000/py-petkit-api
[commits-shield]: https://img.shields.io/github/commit-activity/y/Jezza34000/py-petkit-api.svg?style=flat
[commits]: https://github.com/Jezza34000/py-petkit-api/commits/main
[discord]: https://discord.gg/Va8DrmtweP
[discord-shield]: https://img.shields.io/discord/1318098700379361362.svg?style=for-the-badge&label=Discord&logo=discord&color=5865F2
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge&label=Home%20Assistant%20Community&logo=homeassistant&color=18bcf2
[forum]: https://community.home-assistant.io/t/petkit-integration/834431
[license-shield]: https://img.shields.io/github/license/Jezza34000/py-petkit-api.svg??style=flat
[maintenance-shield]: https://img.shields.io/badge/maintainer-Jezza34000-blue.svg?style=flat
[releases-shield]: https://img.shields.io/github/release/Jezza34000/py-petkit-api.svg?style=for-the-badge&color=41BDF5
[releases]: https://github.com/Jezza34000/py-petkit-api/releases
[github-sponsor-shield]: https://img.shields.io/badge/sponsor-Jezza34000-blue.svg?style=for-the-badge&logo=githubsponsors&color=EA4AAA
[github-sponsor]: https://github.com/sponsors/Jezza34000
[buymeacoffee-shield]: https://img.shields.io/badge/Donate-buy_me_a_coffee-yellow.svg?style=for-the-badge&logo=buy-me-a-coffee
[buymeacoffee]: https://www.buymeacoffee.com/jezza
