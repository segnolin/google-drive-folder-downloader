# -*- coding: utf-8 -*-
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
import os
import pickle
import sys

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def main():

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=1337)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds)

    folder_name = sys.argv[1]
    folder_id = ''
    location = ''
    if len(sys.argv) > 2:
        location = unicode(sys.argv[2], 'utf-8')
        if location[-1] != '/':
            location += '/'

    folder = service.files().list(
            q="name='{}' and mimeType='application/vnd.google-apps.folder'".format(folder_name),
            fields='files(id, name, parents)').execute()

    total = len(folder['files'])
    if total != 1:
        print('{} folders found'.format(total))
        prompt = 'Please select the folder you want to download:\n\n'
        for i in range(total):
            prompt += u'[{}]: {}\n'.format(i, get_full_path(service, folder['files'][i]))
        print prompt
        choice = int(raw_input('Your choice: '))
        if 0 <= choice and choice < total:
            folder_id = folder['files'][choice]['id']
        else:
            sys.exit(1)
    else:
        folder_id = folder['files'][0]['id']

    print('{} {}'.format(folder_id, folder_name))
    download_folder(service, folder_id, location, unicode(folder_name, 'utf-8'))

def get_full_path(service, folder):

    if not 'parents' in folder:
        return folder['name']
    files = service.files().get(fileId=folder['parents'][0], fields='id, name, parents').execute()
    path = files['name'] + ' > ' + folder['name']
    while 'parents' in files:
        files = service.files().get(fileId=files['parents'][0], fields='id, name, parents').execute()
        path = files['name'] + ' > ' + path
    return path

def download_folder(service, folder_id, location, folder_name):

    if not os.path.exists(location + folder_name):
        os.makedirs(location + folder_name)
    location += folder_name + '/'

    result = []
    files = service.files().list(
            pageSize='1000',
            q="'{}' in parents".format(folder_id),
            fields='files(id, name, mimeType)').execute()
    result.extend(files['files'])
    result = sorted(result, key=lambda k: k['name'])

    total = len(result)
    current = 1
    for item in result:
        file_id = item['id']
        filename = item['name']
        mime_type = item['mimeType']
        print file_id, filename, mime_type, '({}/{})'.format(current, total)
        if mime_type == 'application/vnd.google-apps.folder':
            download_folder(service, file_id, location, filename)
        elif not os.path.isfile(location + filename):
            download_file(service, file_id, location, filename)
        current += 1

def download_file(service, file_id, location, filename):

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(location + filename, 'wb')
    downloader = MediaIoBaseDownload(fh, request, 1024 * 1024 * 1024)
    done = False
    while done is False:
        try:
            status, done = downloader.next_chunk()
        except:
            fh.close()
            os.remove(location + filename)
            sys.exit(1)
        print '\rDownload {}%.'.format(int(status.progress() * 100)),
        sys.stdout.flush()
    print ''

if __name__ == '__main__':
    main()
