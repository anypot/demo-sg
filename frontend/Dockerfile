FROM nginx:1.30.6-alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html /usr/share/nginx/html/index.html

# The official image defaults to root; the "nginx" user already exists.
# All writable paths are under /tmp (see nginx.conf), so no chown is needed.
USER nginx

EXPOSE 8080
