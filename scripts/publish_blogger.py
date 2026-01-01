import os
import markdown
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/blogger']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)

        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)

    return build('blogger', 'v3', credentials=creds)

def publish_post(service, blog_id, title, content, labels):
    post = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "labels": labels
    }

    service.posts().insert(blogId=blog_id, body=post, isDraft=False).execute()

if __name__ == "__main__":
    print("Script base criado com sucesso.")
