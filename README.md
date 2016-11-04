# Flask At Scale Tutorial at PyCon 2016

This repository contains the companion code to my PyCon 2016 "Flask At Scale" class.

**IMPORTANT NOTE**: The initial commit in this repository has a version of this application that has a few scalability problems discussed during class. These problems are addressed in subsequent commits.

## Installation

All the code and examples were tested on Python 3.5\. Older versions of Python including 2.7 will likely work as well.

As usual, create a virtual environment and install the requirements with pip.

```
pip install -r requirements.txt
```

## Running

The application uses Flask-Script to simplify common tasks such as starting a development server. To run the application run the following command:

```
python manage.py runserver
```

You can add `--help` to see what other start up options are available.

The second component of this application is the Celery workers, which must be started with the following command:

```
python manage.py celery

%celery -A proj worker --loglevel=INFO --concurrency=10 -n worker1.%h
```

Need to start the RabbitMQ. In Windows, open Console with `Administrator` account, then type `c:\Prog~\...\sbin\RabbitMQ-server.bat restart`.

If you want to have more verbose output from the workers you can add `--loglevel=info` to the command above.

Finally, in addition to the main server and the Celery workers, a message queue must be available to be used for communication between all these processes. By default, a Redis server running on localhost on the default port is assumed. If you want to use a different message queue, or a different configuration for Redis, then set the `CELERY_BROKER_URL` environment variable to the message queue connection URL. See the Celery documentation for information on connection URLs.

## Usage

That application allows multiple users to chat online. You can launch the application on your browser by typing `http://127.0.0.1:5000` on the address bar.

Since authentication is not a topic in this class, I've decided to use a simplified flow that combines the registration and login forms in one. If you are a new user, enter your chosen nickname and password to register. If the nickname was not seen before the server will register you. If you are a returning user, provide your login in the same form. If the nickname is registered then the password will be validated.

Once you are logged in you can type messages in the bottom text entry field, and these messages will be seen by all other users. You can use simple MarkDown formatting to add style to your messages. If you enter any links as part of your message, these will be shown in expanded form below the message.

--------------------------------------------------------------------------------

## Work with Nginx web server

## Run application as wsgi

Need to install the `cygwin` if you plan to run the application on windows. Found `eventlet` issue running app directly under the windows.

### To start

Under the project folder, run `gunicorn -b 127.0.0.1:5000 -k eventlet -w 1 -t 60 volume3d.wsgi` where `-t` is time out option.

## SSL

<http://www.akadia.com/services/ssh_test_certificate.html>

- Generate a private key `openssl genrsa -des3 -out server.key 1024`
- Generate a CSR (certificate Signing Request) `openssl req -new -key server.key -out server.csr`
- Remove passphrase from key `cp server.key server.key.org` `openssl rsa -in server.key.org -out server.key`
- Generate a self-signed certificate `openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt`
- Keep two files: `server.crt`, and `server.key`

### The one finally working

<http://www.booches.nl/2009/09/openssl-cygwin-certificate-authority/>

1. create some folders `mkdir certs private newcerts`
2. preparations `echo 1000 > serial` `touch index.txt`
3. generate CA (Certificate Authority)
    ```bash
    openssl req -new -x 509 -days 3650 \
            -extensions v3_ca \
            -keyout private/cakey.pem –out cacert.pem \
            -config /usr/ssl/openssl.cnf
    ```
   where `openssl.cnf` is the configuration file for the openssl.
4. Generate SSL Request
    ```
    openssl req -sha256 –new –nodes \
              -out cert-www-hui-com.pem \
              -keyout private/priv-www-hui-com.pem \
              -config /usr/ssl/openssl.cnf
    ```
   Here need to input the `Common Name`, use the one of the **hostname** (e.g. `hui-laptop`).
5. Sign CSR (request)
    ```bash
    oenssl ca –config /usr/ssl/openssl.cnf \
              -out sslcert-www-4ip-nl.pem \
              -infiles cert-www-hui-com.pem
    ```
6. pack the certificates (not needed in this example)

   Since the CA is not made by the recognized authority, to pack all the CAs together. **In this case**, there is no intermediate CA, the certificate is sign by the `ROOT` directly.
      ```bash
      cat sslcert-www-hui-com.pem cacert.pem > sslcertAll-www-hui-com.pem
      ```

   Then use the hostname rather than the IP address while connecting. save the two following files in the Nginx configurataion folder

      - `ssl_certificate`: `sslcertAll-www--hui-com.pem`
      - `ssl_certificate_key`: `private\priv-www--hui-com.pem`

    On the client, user may still **need to install the CA** (`cacert.pem`) as `Trusted Root Certification Authorities`

## Config Nginx

<https://www.ibm.com/support/knowledgecenter/SS8JFY_9.0.0/com.ibm.lmt.doc_9.0/com.ibm.license.mgmt.doc/security/t_ca_private.html>

<https://www.ibm.com/support/knowledgecenter/en/SS8JFY_9.0.0/com.ibm.lmt.doc_9.0/com.ibm.license.mgmt.doc/security/t_ca_existing.html#t_ca_existing__keygen>
