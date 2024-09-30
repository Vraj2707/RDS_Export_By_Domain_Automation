
# Export Automation Script

**Version 1.0**

## Overview

This project automates the tedious and time-consuming manual process of exporting csv files of the codelists from the Informatica platform. Instead of manually performing the steps required to extract CSV files, this automation takes user inputs (environment and domain) and generates a zip file containing all relevant CSV files, significantly simplifying the workflow. It is designed to streamline data export for developers and administrators working across different environments like DEV, UAT, and PROD.

## Features

- Automates file export process from Informatica
- Supports different environments: DEV, UAT, and PROD
- Outputs a compressed zip file containing all the CSV files
- Clear logging of all steps being performed during the execution

## Prerequisites

Before running the project, make sure you have the following installed and set up:

1. **Python**: Version >= 3.0
2. **API Credentials and Certificates**: Required for accessing the application API.  
   _Note_: You will need to request credentials and certificates from the team. These should be placed in a folder named **"API_Data"** in the same directory as the Python script.

## Installation & Setup

### 1. Clone the repository

To start with, clone this repository using the following command:

```
git clone https://github.com/Vraj2707/RDS_Export_By_Domain_Automation.git
cd Export Automation Script
```

### 2. Prepare the API Credentials and Certificates

Make sure to place your **credentials** and **certificates** (provided by the team) inside a folder named **"API_Data"** in the same directory as the \`ExportAutomation.py\` script.

```
/project-directory
    ├── ExportAutomation.py
    ├── API_Data/
    │   ├── credentials.json
    │   └── certificates.pem
```

### 3. Run the Script

Now you can run the script by opening your terminal and using the following command:

```
python ExportAutomation.py
```

## Usage

1. **Select Environment**: The script will prompt you to select the environment. You can choose from `DEV`, `UAT`, or `PROD`.
2. **Provide Domain Input**: After selecting the environment, provide the key of the domain (For Example: DOMAIN (dmn)) - then write the key `dmn`.
3. **Observe Progress**: The script will display all the steps it is performing.
4. **Output**: Once completed, a zip file will be generated in the same directory containing all the CSV files.

### Example:

<img width="403" alt="a" src="https://github.com/user-attachments/assets/cff39fff-7fd4-4d03-896b-6ba083744612">

---

<img width="580" alt="b" src="https://github.com/user-attachments/assets/233afdbf-554f-4444-98cf-bcac93a0a994">

## Future Enhancements (To-Do)

For Version 2.0:
- **Auto-Recovery from API Request Failures**: Implement logic to handle and recover from API request timeouts or failures.

---
