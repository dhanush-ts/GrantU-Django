# utils.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
import datetime

class Helper:
    def create_gmeet_link(self,connection, start_time, end_time,description="Mentorship Session"):
        credentials = service_account.Credentials.from_service_account_file(
            'utils/grantu-1291e8c1173b.json',
            scopes=['https://www.googleapis.com/auth/calendar'],
        ).with_subject('admin@grantu.education')  
        service = build('calendar', 'v3', credentials=credentials)

        event = {
            'summary': f'Mentorship Connection: {connection.Mentor.First_Name} & {connection.Mentee.First_Name}',
            'description': description,
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'attendees': [
                {'email': connection.Mentor.Email_Address},
                {'email': connection.Mentee.Email_Address},
            ],
            'conferenceData': {
                'createRequest': {
                    'requestId': f"{connection.Connection_ID}-meet",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            },
        }
        
        event = service.events().insert(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            body=event,
            conferenceDataVersion=1,
            sendUpdates='all'  # This sends emails to attendees
        ).execute()


        return event['hangoutLink']