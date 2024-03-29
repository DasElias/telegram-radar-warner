# telegram_radar_warner

The purpose of this Python is to query a Telegram chat for the recent messenges and provide them in the form of an API as JSON and plaintext. It was developed to get the latest data about radar warners from a Telegram group and provide this data as shortcut command in iOS, since it's not possible to get Telegram-chats there. 

## Getting started
1) [Log into your Telegram account](https://my.telegram.org/) and create a new application. On this site, you can obtain your API ID and your API hash.
2) Rename the file `.env.example` to `.env` and fill in your credentials along with the name of the chat to monitor or the invitation link to the Telegram group as well as your phone number.
3) Activate your configured virtual environment and install all necessary dependencies (see below). 
4) **Run the application** via `python main.py`. 
3) On the first time you start the application, it is necessary to fill in your login code. You will receive this code via Telegram at the telephone number you entered in the ".env"-file. Call the GET-endpoint `/login?key=...` with the key you obtained.
4) Afterwards, you are ready to query the recent messenges via the endpoints `/messages/text` and `/messages/json`. 

## Python Virtual Environments

It is recommended to run this project in a Python virtual environment. To do so, it is necessary to install venv and then create a new env first:

```
sudo apt-get install python3-venv
python3 -m pip install virtualenv
python3 -m venv radarwarner
```

Afterwards, it is possible to open the environment in the project folder by entering:

```
source radarwarner/bin/activate
```

On Windows, you can open the environment with:
```	
.\venv\Scripts\activate
```

In this mode, the dependencies can then be installed.

## Dependencies

- python3
- telethon
```
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade telethon
``` 
- python-dotenv
```
pip install python-dotenv
```
- pytz
```
pip install pytz
```
- Aeros
```
pip install hypercorn==0.12.0
pip install Aeros==0.3.1
```
- emoji
```
pip install emoji==1.7.0
```
- python-dateutil
```
pip install python-dateutil
```

## How the replacement works
This application not only takes the raw mesages from the Telegram chat and outputs them, but rather they are pre-processed. The following steps are performed:

- if the message is only a picture, a voice message or another file, return a descriptive string
- truncate the message to a maximum of of `MAX_MESSAGE_LENGTH` characters
- replacements are performed as specified in `replacements.csv`
- remove emojis
- if `speakpunctuation` flag is set, replace some punctuation marks with their spoken equivalent
- if a message was sent in reply to another one, replacements are done for this message too
- the parsed message is assembled by concatenating the time of the message, the content of the reply_to message and the content of the current message
- check whether the message should be filtered
- if the last message was sent by the same user, concatenate the two messages
- when the next message after the last picked message would not be filtered, has text content and would be concatenated since it was sent by the same user, it gets concatenated too
- all messages, that are only multimedia messages without content are filtered too, but summaried to one single message which is appended at the end of the output

## replacements.csv
The purpose of this file is to replace certain strings in the messages. It is a CSV file in the following format:
```	
<what to replace>,<replacement>
```

This file can be generated using the util script in the `generate_replacements`-folder (`generate.py`).

To run this script, please enter the virtual environment as desribed above and install the additional dependencies:
```
pip install pandas
pip install openpyxl
```

This script takes the file `source.xlsx` as input and generates the file `replacements.csv` as output. Using the `source.xlsx` file, it is possible to specify your own replacements. 