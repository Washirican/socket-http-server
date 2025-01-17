import mimetypes
import socket
import sys
import traceback
import ntpath
import os


def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    """
    return b'\r\n'.join([
        b'HTTP/1.1 200 OK',
        b'Content-Type: ' + mimetype,
        b'',
        body
        ])


def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""
    return b'\r\n'.join([
        b'HTTP/1.1 405 Method Not Allowed response',
        b'',
        b"You can't do that on this server!"
        ])


def response_not_found(path):
    """Returns a 404 Not Found response"""
    return b'\r\n'.join([
        b'HTTP/1.1 404 Error encountered while visiting ' + ntpath.basename(path).encode('utf-8')
        ])


def parse_request(request):
    """
    Given the content of an HTTP request, returns the path of that request.

    This server only handles GET requests, so this method shall raise a
    NotImplementedError if the method of the request is not GET.
    """

    method, path, version = request.split('\r\n')[0].split(' ')

    if method != 'GET':
        raise NotImplementedError

    return path


def response_path(path):
    """
    This method should return appropriate content and a mime type.

    If the requested path is a directory, then the content should be a
    plain-text listing of the contents with mimetype `text/plain`.

    If the path is a file, it should return the contents of that file
    and its correct mimetype.

    If the path does not map to a real location, it should raise an
    exception that the server can catch to return a 404 response.

    Ex:
        response_path('/a_web_page.html') -> (b"<html><h1>North Carolina...",
                                            b"text/html")

        response_path('/images/sample_1.png')
                        -> (b"A12BCF...",  # contents of sample_1.png
                            b"image/png")

        response_path('/') -> (b"images/, a_web_page.html, make_type.py,...",
                             b"text/plain")

        response_path('/a_page_that_doesnt_exist.html') -> Raises a NameError

    """

    fullpath = 'webroot' + path
    filename = ntpath.basename(path)

    mime_type = b''
    if not os.path.isfile(fullpath):
        try:
            files = ''
            for x in os.listdir(fullpath):
                files += str(x) + '\r\n'

            mime_type = b'text/plain'
            content = b'' + files.encode('utf-8')
        except FileNotFoundError:
            content = response_not_found(fullpath)

    else:
        try:
            with open(fullpath, "rb") as f:
                byte = f.read()

                mime_type = mimetypes.guess_type(filename)[0].encode()
                content = byte
        except NameError:
            content = response_not_found(fullpath)

    return content, mime_type


def server(log_buffer=sys.stderr):
    address = ('localhost', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    print("making a server on {0}:{1}".format(*address), file=log_buffer)

    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        break

                print("Request received:\n{}\n\n".format(request))

                try:
                    path = parse_request(request)
                    # print('URL: {}'.format(path))

                    content, mime_type = response_path(path)

                    # print(f'Content: {content}')
                    # print(f'Mime-Type: {mime_type}')

                    response = response_ok(
                        body=content,
                        mimetype=mime_type
                        )

                except NotImplementedError:
                    response = response_method_not_allowed()

                print('sending response...', file=log_buffer)
                conn.sendall(response)

            except:
                traceback.print_exc()

            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)
