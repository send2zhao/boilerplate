## Hui's version of server-running
Run this shell directly under the folder which holds `volume3d`
(i.e. ../volume3d)

## for information of running front-end webserver, Nginx,  as reverse proxy
## see notes in `webserver/nginx/readme.md`

## In windows: should run under the cygwin

gunicorn -b 127.0.0.1:5000 -k eventlet -w 1 -t 60 volume3d.wsgi
