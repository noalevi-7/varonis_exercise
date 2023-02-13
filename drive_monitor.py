import datetime
import os.path

from apscheduler.schedulers.blocking import BlockingScheduler
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly",
          "https://www.googleapis.com/auth/drive.activity.readonly",
          "https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.file"]

CREATE = "create"
ANYONE_WITH_LINK = "anyoneWithLink"
ID = "id"
DOMAIN = "domain"
TYPE = "type"
USER = "user"
GROUP = "group"
ROLE = "role"
ONE_DAY = 86400


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # V3 API (files & permissions)
    service_v3 = build("drive", "v3", credentials=creds)

    # V2 API (activity)
    service_v2 = build("driveactivity", "v2", credentials=creds)

    monitor_file_creation_for_the_day_before(service_v3, service_v2)


def monitor_file_creation_for_the_day_before(service_v3, service_v2):
    try:
        milliseconds = get_milliseconds_for_yesterday()
        results_activity = service_v2.activity().query(body={"pageSize": 10,
                                                             "filter": "time > {0}".format(milliseconds)}).execute()
        activities = results_activity.get("activities", [])

        dict_of_create_files = get_all_create_file_activities(activities)
        remove_public_permissions_and_print_sharing_status(dict_of_create_files, service_v3)

    except HttpError as error:
        print(f"An error occurred: {error}")


def get_milliseconds_for_yesterday():
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    date = yesterday - datetime.datetime(1970, 1, 1)
    return round((date.total_seconds()) * 1000)


def get_all_create_file_activities(activities):
    dict_of_create_activities = {}

    if not activities:
        return None
    else:
        for activity in activities:
            action = get_action_info(activity["primaryActionDetail"])
            file_id = get_file_id(activity["targets"][0])

            if action == CREATE:
                dict_of_create_activities[file_id] = activity
    return dict_of_create_activities


def remove_public_permissions_and_print_sharing_status(dict_of_create_files, service_v3):
    print("File creation summary for the past day\n")
    for file_id, activity in dict_of_create_files.items():
        if is_not_file(activity):
            continue
        permissions = service_v3.permissions().list(fileId=file_id).execute()["permissions"]

        file_name = service_v3.files().get(fileId=file_id).execute()["name"]
        print("{0} - sharing status:".format(file_name))

        for permission in permissions:
            if permission[TYPE] == USER:
                print("    - Has user access for user id {0}, with {1} role\n".
                      format(permission[ID], permission[ROLE]))

            elif permission[TYPE] == GROUP:
                print("    - Has group access for group id {0}, with {1} role\n".
                      format(permission[ID], permission[ROLE]))

            elif permission[TYPE] == DOMAIN:
                print("    - Has domain access for domain {0}, with {1} role\n".
                      format(permission[DOMAIN], permission[ROLE]))

            elif permission[ID] == ANYONE_WITH_LINK:
                if len(permissions) > 1:
                    service_v3.permissions().delete(fileId=file_id, permissionId="anyoneWithLink").execute()
                    print("    - Had Public access, removed by the program")
                else:
                    print("ERROR: file can't have only public permission")
    print("\n")


def is_not_file(activity):
    return 'file' not in activity['targets'][0]['driveItem'].keys()


# Returns the name of a set property in an object, or else "unknown".
def get_one_of(obj):
    for key in obj:
        return key
    return "unknown"


# Returns the type of action.
def get_action_info(action_detail):
    return get_one_of(action_detail)


def get_file_id(target):
    if "driveItem" in target:
        file_id = target["driveItem"].get("name", "unknown")[6:]
        return file_id
    return "unknown"


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(main, 'cron', hour='12', minute='00')
    scheduler.start()
