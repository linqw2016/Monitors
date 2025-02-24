# BDAccountMonitor

## Overview
BDAccountMonitor is a Python project designed to monitor various accounts across different regions. It probes the accounts to check their connectivity and handles incidents when connectivity issues arise.

## Project Structure
```
BDAccountMonitor
├── src
│   ├── probe.py          # Logic for probing accounts and handling incidents
│   ├── bd_account_monitor.py  # Manages monitoring of multiple accounts
│   └── utils.py          # Utility functions for retries and asynchronous handling
├── requirements.txt      # Project dependencies
├── .gitignore            # Files and directories to ignore in Git
└── README.md             # Project documentation
```

## Installation
To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd BDAccountMonitor
pip install -r requirements.txt
```

## Usage
To run the account monitoring, execute the `bd_account_monitor.py` script. This will initialize the accounts based on the specified region and start probing them.

```bash
python src/bd_account_monitor.py
```

## Functions
- **Probing Logic**: The `probe.py` file contains the main logic for probing accounts, including DNS resolution and HTTP requests.
- **Incident Handling**: The project includes functionality to create incidents when connectivity issues are detected.
- **Job Management**: The `bd_account_monitor.py` file manages the submission of probe jobs and checks their statuses.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.