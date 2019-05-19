# -*- coding: utf-8 -*-
from apiclient import errors
from apiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import io
import os
import sys

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'

def main():
    """
    Download folder content from google dirve without zipping.
    """
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))

    folder_name = sys.argv[1]
    folder_id = ''
    location = ''
    if len(sys.argv) > 2:
        location = unicode(sys.argv[2], 'utf-8')
        if location[-1] != '/':
            location += '/'
    try:
        folder = service.files().list(
                q="name='{}' and mimeType='application/vnd.google-apps.folder'".format(folder_name),
                fields='files(id)').execute()
        folder_id = folder['files'][0][u'id']
        print folder_id
        folder_name = unicode(folder_name, 'utf-8')
        download_folder(service, folder_id, location, folder_name)

    except errors.HttpError, error:
        print 'An error occurred: {}'.format(error)

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
    result = sorted(result, key=lambda k: k[u'name'])

    total = len(result)
    current = 1
    for item in result:
        file_id = item[u'id']
        filename = item[u'name']
        mime_type = item[u'mimeType']
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
        status, done = downloader.next_chunk()
        print '\rDownload {}%.'.format(int(status.progress() * 100)),
        sys.stdout.flush()
    print ''

if __name__ == '__main__':
    main()
