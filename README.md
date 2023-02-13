# Google Drive Monitor - Varonis exercise

Simple Python command-line application that makes requests to the Drive V2 / V3 API,
so you can monitor once a day for new files creation and manage their permissions.



## Prerequisites
- Python
- Activate the Drive API in the Google API Console([the detail page](https://developers.google.com/workspace/guides/create-project/))
- Enable `Drive API` and `Drive Activity API`
- Create a OAuth client ID credential and download the json file ([the detail page](https://developers.google.com/workspace/guides/create-credentials/))
- Rename the json file to - credentials.json

## Install 
```
pip install -r requirements.txt
```

## Run
```
python drive_monitor.py
```
- This program runs once a day by scheduler engine, and checks for file creation that happened the day before.
- For every file creation the program checks its permissions, if this file has `anyone` access, the program removes this permit.
- The program prints out the sharing status for each file it checks.
### output examples 
```
File creation summary for the past day

readme - sharing status:
    - Has user access for user id 07010884606913906718, with owner role
fmd - sharing status:
    - Has user access for user id 07010884606913906718, with owner role
shared_with_uri - sharing status:
    - Has user access for user id 10758064074363540534, with writer role
    - Has user access for user id 07010884606913906718, with owner role
```

```
File creation summary for the past day

new_file_public - sharing status:
    - Had Public access, removed by the program
    - Has user access for user id 07010884606913906718, with owner role
readme - sharing status:
    - Had Public access, removed by the program
    - Has user access for user id 07010884606913906718, with owner role
fmd - sharing status:
    - Had Public access, removed by the program
    - Has user access for user id 07010884606913906718, with owner role
```

## Notes
- On your first run, you will be prompted to log in. If you are logged into multiple Google accounts, you will be asked to select one account to use for the authorization.
- I've tried to translate the `user_id` into `user_name` without success. I've notice the option to get `user_id` by giving the `email`, so it will be possible to ask for all company emails in order to be able to translate them into `user id`, and therefore the log will be more readable.
- I've tried to retrieve the default sharing settings without success. For non-company accounts the default sharing settings is `Restricted`, but I did not find the relevant documentation in order to request this info.
This settings can be changed if you are a GSuit administrator for your company, you can change it to `anyone at my organisation`. If I have an account that can change these settings I would do it from the web app and look on the `F12 Network Window` to see the relevant request, and add this to my program.
- Referring to attack surface in google drive, the attacker only needs the `credentials.json` file, that sometimes saved on the user's computer, in order to connect the google drive api and from there he can do whatever he wants, steal files, change permissions or even add malware file.
