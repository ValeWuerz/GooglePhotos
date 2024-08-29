from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import requests
# Scopes for the API
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds
def list_albums(service):
    results = service.albums().list(
        pageSize=10).execute()
    albums = results.get('albums', [])
    for album in albums:
        print(f"Album title: {album['title']}")
def list_album_images(service, album_id):
    all_items = []
    next_page_token = None
    
    while True:
        results = service.mediaItems().search(body={"albumId": album_id, "pageToken": next_page_token}).execute()
        items = results.get('mediaItems', [])
        all_items.extend(items)
        next_page_token = results.get('nextPageToken')
        
        if not next_page_token:
            break
    
    return all_items
def get_album_id_by_title(service, album_title):
    # Get a list of albums
    results = service.albums().list(pageSize=50).execute()
    albums = results.get('albums', [])

    # Find the album with the given title
    for album in albums:
        if album['title'].lower() == album_title.lower():
            return album['id']
def download_image(image_url, filename):
    image_url += "=d"  # Append '=d' to download full-resolution image
    response = requests.get(image_url)
    
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download {filename}. Status code: {response.status_code}")

    return None
if __name__ == '__main__':
    creds = authenticate()
    try:
        service = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)
        print("Google Photos Library API service created successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
    list_albums(service)
    album_title = 'haare'
    album_id = get_album_id_by_title(service, album_title)
    if album_id:
        print(f"Album '{album_title}' found with ID: {album_id}")
        save_directory = 'downloaded_images'
        os.makedirs(save_directory, exist_ok=True)
        images=list_album_images(service, album_id)
        if images:
            print(f"Found {len(images)} images in the album.")
            for image in images:
                filename = os.path.join(save_directory, f"{image['filename']}.jpg")
                download_image(image['baseUrl'], filename)
        else:
            print("No images found in the album.")
    else:
        print(f"Album '{album_title}' not found.")