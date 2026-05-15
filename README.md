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

## 💡 Usage :

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

        # Read or do an action ...

if __name__ == "__main__":
    asyncio.run(main())
```

### 📑 Reading devices informations :

```python
        print(client.petkit_entities[device_id])
```

### 📡 Available commands

Below is a reference of commands available via `send_api_request()` and `bluetooth_manager.send_ble_command()`

---

### `DeviceCommand.UPDATE_SETTING`

Updates one or more device settings by sending a key-value payload to the device configuration endpoint.

```python
await client.send_api_request(device_id, DeviceCommand.UPDATE_SETTING, {"payload_key": value})
```

| Payload key         | Values   | Description                               |
| ------------------- | -------- | ----------------------------------------- |
| `lightMode`         | `0/1`    | Indicator light / display on/off          |
| `manualLock`        | `0/1`    | Child lock on/off                         |
| `camera`            | `0/1`    | Camera on/off                             |
| `disturbMode`       | `0/1`    | Do not disturb on/off                     |
| `highlight`         | `0/1`    | Pet tracking on/off                       |
| `timeDisplay`       | `0/1`    | Video timestamp on/off                    |
| `microphone`        | `0/1`    | Microphone on/off                         |
| `night`             | `0/1`    | Night vision on/off                       |
| `lackLiquidNotify`  | `0/1`    | Lack of liquid notification on/off        |
| `systemSoundEnable` | `0/1`    | System notification sounds on/off         |
| `foodWarn`          | `0/1`    | Food shortage alarm on/off                |
| `feedTone`          | `0/1`    | Feed tone on/off                          |
| `feedSound`         | `0/1`    | Feed sound on/off                         |
| `feedNotify`        | `0/1`    | Dispensing notification on/off            |
| `foodNotify`        | `0/1`    | Refill notification on/off                |
| `petNotify`         | `0/1`    | Pet visit notification on/off             |
| `eatNotify`         | `0/1`    | Pet eating notification on/off            |
| `moveNotify`        | `0/1`    | Movement detection notification on/off    |
| `lowBatteryNotify`  | `0/1`    | Low battery notification on/off           |
| `soundEnable`       | `0/1`    | Voice dispense sound on/off               |
| `desiccantNotify`   | `0/1`    | Desiccant replacement notification on/off |
| `volume`            | `1–9`    | Speaker volume level                      |
| `surplus`           | `20–100` | Surplus food threshold (D3)               |
| `shortest`          | `3–60`   | Minimum eating duration in seconds (D4S)  |
| `surplusControl`    | `0/1`    | Surplus controle on/off                   |
| `surplusStandard`   | `N`      | Surplus food control level                |
| `eatSensitivity`    | `N`      | Eat detection sensitivity (AI)            |
| `petSensitivity`    | `N`      | Pet detection sensitivity (AI)            |
| `moveSensitivity`   | `N`      | Move detection sensitivity (AI)           |
| `sandType`          | `N`      | Litter type selection                     |
| `autoIntervalMin`   | `N`      | Repeat cleaning interval in minutes       |
| `stillTime`         | `N`      | Cleaning delay in seconds after pet exits |
| `deepSpray`         | `0/1`    | Deep deodorizing on/off (T5/T6)           |
| `sandSaving`        | `0/1`    | Sand saving mode on/off                   |
| `bury`              | `0/1`    | Waste covering on/off                     |
| `litterFullNotify`  | `0/1`    | Litter full notification on/off           |
| `petInNotify`       | `0/1`    | Pet entry notification on/off             |
| `workNotify`        | `0/1`    | Cleaning cycle notification on/off        |
| `deodorantNotify`   | `0/1`    | Deodorant (N50) low notification on/off   |
| `sprayNotify`       | `0/1`    | Deodorant (N60) low notification on/off   |
| `lackSandNotify`    | `0/1`    | Lack of litter notification on/off        |
| `logNotify`         | `0/1`    | Work log notification on/off              |
| `lightAssist`       | `0/1`    | Light assist on/off                       |
| `cameraLight`       | `0/1`    | Camera light on/off                       |
| `toiletNotify`      | `0/1`    | Pet toileting notification on/off         |
| `toiletLight`       | `0/1`    | Toilet light on/off                       |
| `homeMode`          | `0/1`    | Privacy mode on/off                       |
| `cameraOff`         | `0/1`    | Privacy — camera off on/off               |
| `cameraInward`      | `0/1`    | Privacy — camera inward on/off (T6)       |
| `noSound`           | `0/1`    | Privacy — microphone off on/off           |
| `phDetection`       | `0/1`    | AI urinary pH detection on/off            |
| `voice`             | `0/1`    | AI yowling detection on/off               |
| `softMode`          | `0/1`    | AI soft stool detection on/off            |

> **IMPORTANT** You can check whether a command is supported by a specific device type/model in `client.petkit_entities[device_id].settings`

> **Note for FEEDER_MINI:** some keys use a dotted path prefix: `settings.lightMode`, `settings.manualLock`, `settings.feedNotify`, `settings.foodNotify`, `settings.desiccantNotify`.

---

### `DeviceCommand.CONTROL_DEVICE`

Sends a control action to the device, typically used to trigger operations such as cleaning, maintenance, or power control.

```python
await client.send_api_request(device_id, DeviceCommand.CONTROL_DEVICE, {DeviceAction.START: LBCommand.CLEANING})
```

| Payload                                            | Description                          |
| -------------------------------------------------- | ------------------------------------ |
| `{DeviceAction.START: LBCommand.CLEANING}`         | Start a scooping/cleaning cycle      |
| `{DeviceAction.START: LBCommand.MAINTENANCE}`      | Enter maintenance mode (T4, T5)      |
| `{DeviceAction.END: LBCommand.MAINTENANCE}`        | Exit maintenance mode (T4, T5)       |
| `{DeviceAction.START: LBCommand.DUMPING}`          | Dump litter into the waste drawer    |
| `{DeviceAction.STOP: work_mode}`                   | Pause the current operation          |
| `{DeviceAction.CONTINUE: work_mode}`               | Resume a paused operation            |
| `{DeviceAction.END: work_mode}`                    | Reset/abort the current operation    |
| `{DeviceAction.START: LBCommand.ODOR_REMOVAL}`     | Trigger deodorizing (T3, T4, T5, T7) |
| `{DeviceAction.START: LBCommand.RESET_N60_DEODOR}` | Reset N60 deodorizer counter         |
| `{DeviceAction.START: LBCommand.LEVELING}`         | Level the litter surface             |
| `{DeviceAction.POWER: 0/1}`                        | Turn purifier on/off (K2)            |
| `{DeviceAction.MODE: N}`                           | Set purifier operating mode (K2)     |

> **work_mode**: You need to pass the current working mode, which can be found in `client.petkit_entities[device_id].state.work_state.work_mode`

---

### `FeederCommand.MANUAL_FEED`

Triggers an immediate manual food dispensing from the feeder with the specified amount.

```python
await client.send_api_request(device_id, FeederCommand.MANUAL_FEED, {"amount": 10})
```

| Payload                        | Description                                        |
| ------------------------------ | -------------------------------------------------- |
| `{"amount": N}`                | Single hopper — dispense N grams/portions          |
| `{"amount1": N, "amount2": 0}` | Dual hopper — dispense from left side only         |
| `{"amount1": 0, "amount2": N}` | Dual hopper — dispense from right side only        |
| `{"amount1": 1, "amount2": 2}` | Dual hopper — dispense from both side at same time |

---

### `FeederCommand.RESET_DESICCANT`

Resets the desiccant replacement timer after the desiccant pack has been replaced.

```python
await client.send_api_request(device_id, FeederCommand.RESET_DESICCANT)
```

---

### `FeederCommand.CANCEL_MANUAL_FEED`

Cancels the ongoing or scheduled manual feed dispensing operation.

```python
await client.send_api_request(device_id, FeederCommand.CANCEL_MANUAL_FEED)
```

---

### `FeederCommand.CALL_PET`

Plays an audio call sound to attract the pet towards the feeder (D3 only).

```python
await client.send_api_request(device_id, FeederCommand.CALL_PET)
```

---

### `FeederCommand.FOOD_REPLENISHED`

Notifies the device that the food hopper has been refilled, resetting the food level indicator.

```python
await client.send_api_request(device_id, FeederCommand.FOOD_REPLENISHED)
```

---

### `FeederCommand.PLAY_SOUND`

Plays the currently selected custom sound on the feeder speaker (D4H, D4SH).

```python
await client.send_api_request(device_id, FeederCommand.PLAY_SOUND, device.settings.selected_sound)
```

---

### `LitterCommand.RESET_N50_DEODORIZER`

Resets the usage counter of the N50 odor eliminator cartridge after it has been replaced.

```python
await client.send_api_request(device_id, LitterCommand.RESET_N50_DEODORIZER)
```

---

### `FountainAction.RESET_FILTER` _(need a BLE relay)_

Sends a BLE command to the water fountain to reset the filter replacement counter.

```python
await client.bluetooth_manager.send_ble_command(device_id, FountainAction.RESET_FILTER)
```

---

### `FountainAction.PAUSE` _(need a BLE relay)_

Sends a BLE command to pause the water fountain pump while it is currently running.

```python
await client.bluetooth_manager.send_ble_command(device_id, FountainAction.PAUSE)
```

---

### `FountainAction.CONTINUE` _(need a BLE relay)_

Sends a BLE command to resume the water fountain pump after it has been paused.

```python
await client.bluetooth_manager.send_ble_command(device_id, FountainAction.CONTINUE)
```

---

### `PetCommand.PET_UPDATE_SETTING`

Updates a pet profile attribute such as the pet's weight stored in the PetKit account.

```python
await client.send_api_request(pet_id, PetCommand.PET_UPDATE_SETTING, {"weight": 4500})
```

| Payload key | Values      | Description                |
| ----------- | ----------- | -------------------------- |
| `weight`    | `N` (grams) | Pet's body weight in grams |

---

### `PetCommand.UPDATE_USAGE_RECORD`

Updates a litter box usage record with the correct pet ID.

```python
await client.send_api_request(pet_id, PetCommand.UPDATE_USAGE_RECORD, {
    "old_pet_id": "ID_OLD",
    "device_id": device_id,
    "time_out": time,
})
```

| Payload key  | Values                   | Description                       |
| ------------ | ------------------------ | --------------------------------- |
| `old_pet_id` | `ID_OLD` (string)        | The pet ID to replace             |
| `device_id`  | `device_id` (string)     | The litter box device ID          |
| `time_out`   | `TIME` (epoch timestamp) | Out timestamp of the usage record |

---

## 💡 More example usage

Check at all the usage in the Home Assistant integration's code : [here](https://github.com/Jezza34000/homeassistant_petkit)

## ☑️ Supported Devices

- **[Supported Devices](https://github.com/Jezza34000/homeassistant_petkit/wiki/Supported-Devices)**

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
