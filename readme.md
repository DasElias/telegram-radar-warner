# telegram_radar_warner

The purpose of this Python is to query a Telegram chat for the recent messenges and provide them in the form of an API as JSON and plaintext. It was developed to get the latest data about radar warners from a Telegram group and provide this data as shortcut command in iOS, since it's not possible to get Telegram-chats there. 

## Getting started
1) [Log into your Telegram account](https://my.telegram.org/) and create a new application. On this site, you can obtain your API ID and your API hash.
2) Rename the file ".env.example" to ".env" and fill in your credentials along with a link to the Telegram group and your phone number.
3) On the first time you start the application, it is necessary to fill in your login code. You will receive this code via Telegram at the telephone number you entered in the ".env"-file. Call the GET-endpoint `/login?key=...` with the key you obtained.
4) Afterwards, you are ready to query the recent messenges via the endpoints `/messages/text` and `/messages/json`. 

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
- flask
```
pip install Flask
```