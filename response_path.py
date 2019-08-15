import mimetypes
import socket
import sys
import traceback
import ntpath


def response_path(path): 
    print(f'Input Path: {path}')
    filename = ntpath.basename(path)
    print('Input Filename: ' + filename)

    with open(path, "rb") as f:
        byte = f.read()
     
    content = byte
    mime_type = mimetypes.guess_type(filename)[0].encode()

    return content, mime_type


if __name__ == '__main__':
    content, mime_type = response_path('webroot/sample.txt')
    print(f'Content: {content}')
    print(f'Mime-Type: {mime_type}')
