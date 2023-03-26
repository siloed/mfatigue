# mfatigue
A proof-of-concept Python script to cause MFA fatigue for known O365 credentials.

> This project is intended strictly for educational, authorised testing, and research purposes only. 

> The author does not assume any responsibility for the use of this project. 

> By using this project, you agree to use it at your own risk and acknowledge that the author is not liable for any misuse, damage, or legal consequences that may arise from its use.

# ToC

- [Introduction](#introduction)
  - [Features](#features)
  - [Limitations](#limitations)
- [Setup](#setup)
- [Usage](#usage)

## Introduction

mfatigue is tool that attempts MFA fatigue on known O365 credentials.

Once a valid O365 username and password is provided, mfatigue will authenticate with those credentials and keep sending MFA push notifications until either the user accepts it, or it hits a limit you specify.

If the user does accept a push, mfatigue will give you a browser window with the fully authenticated O365 session. Additionally, it dumps the session cookies in a format that can be imported easily in browser.

### Features

Current development can handle the following authentication types:
* Azure Active Directory (Azure AD) authentication.
* Active Directory Federation Services (AD FS) redirected authentication.
* Okta redirected authentication.

### Limitations

* Works only with MFA push notifications.
* Will not work if MFA uses code/number entry etc.


## Setup

```sh
# First, upgrade your pip version to latest (optional)
python3 -m pip install --upgrade pip

# Create a folder for python3 virtual environments, if you don't  have one already
mkdir ~/my-python-venvs

# Change to your venv folder
cd ~/my-python-venvs

# Create a new python3 virtual-env for mfatigue tool
python3 -m venv mfatique_venv
source ./mfatique_venv/bin/activate

# install the pip requirements
python3 -m pip install -r requirements.txt

# now you can run the tool to confirm installation
python3 ./mfatigue.py 
```

## Usage

<h2 align="center">
  <img src="static/mfatigue_usage.png" alt="mfatigue_usage" width="90%">
  <br>
</h2>


