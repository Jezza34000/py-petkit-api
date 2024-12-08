# Petkit Api Client

[![PyPI](https://img.shields.io/pypi/v/pypetkitapi.svg)][pypi_]
[![Python Version](https://img.shields.io/pypi/pyversions/pypetkitapi)][python version]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

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

## Usage:

```python
from petkit import PetKitClient

# Create a new PetKitClient instance
client = PetKitClient()

# Login to the PetKit API
client.login('username', 'password', 'region', 'timezone')
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
