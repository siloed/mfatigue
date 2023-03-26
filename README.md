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
  - [Quick Start](#quick-start)
  - [CLI Help](#cli-help)

# Introduction

mfatigue is tool that attempts MFA fatigue on known O365 credentials.

Once a valid O365 username and password is provided, mfatigue will authenticate with those credentials and keep sending MFA push notifications until either the user accepts it, or it hits a limit you specify.

If the user does accept a push, mfatigue will give you a browser window with the fully authenticated O365 session. Additionally, it dumps the session cookies in a format that can be imported easily in browser.

## Features

Current development can handle the following authentication types:
* Azure Active Directory (Azure AD) authentication.
* Active Directory Federation Services (AD FS) redirected authentication.
* Okta redirected authentication.

## Limitations

* Works only with MFA push notifications.
* Will not work if MFA uses code/number entry etc.


# Setup

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

# Usage

## Quick Start
<h2 align="center">
  <img src="static/mfatigue_usage.png" alt="mfatigue_usage" width="90%">
  <br>
</h2>

**Example #1 : Basic usage with a known O365 username and password:** <br />
-- The following will attempt 3 x MFA push notifications (default), each with a 55 second (default) wait for user acceptance.
```sh
python3 ./mfatigue.py -u targetuser@randomtestdomain.com -p "P@ssword123"
```

**Example #2 : Alternatively, for a complex password, you can provide it as an input file (--single-pass-file):** <br />
-- Same as example #1 above, with the password read from the first line of the given text file.
```sh
python3 ./mfatigue.py -u targetuser@randomtestdomain.com -spf ./password.txt
```

**Example #3 : When required, you can specify additional parameters such as max mfa attempts and mfa wait period:** <br />
-- In the example below we are attemping 10 x MFA push notificatons, each with a 30 second wait for user acceptance.
```sh
python3 ./mfatigue.py -u targetuser@randomtestdomain.com -spf ./password.txt -max-mfa 10 --max-mfa-wait 30
```

## CLI Help
```
mfatigue Usage:
  python3 ./mfatigue.py -u USERNAME [-p PASSWORD] [-spf SINGLE_PASS_FILE] [--max-mfa MAX_MFA] [--max-mfa-wait MAX_MFA_WAIT]

Help:
  python3 ./mfatigue.py --help
  
Options:
  -h, --help                                                    show this help message and exit
  -u USERNAME, --username USERNAME                              Username
  -p PASSWORD, --password PASSWORD                              Password
  -spf SINGLE_PASS_FILE, --single-pass-file SINGLE_PASS_FILE    Single password textfile. Password should be in the first line.
  --max-mfa MAX_MFA                                             Max MFA pushes (Default: 3)
  --max-mfa-wait MAX_MFA_WAIT                                   Max wait period for an MFA push accept before sending another. (Default: 55 seconds)
```
