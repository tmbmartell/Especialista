FROM nginx:1.27-alpine
COPY apps/web/index.html /usr/share/nginx/html/index.html
COPY apps/web/styles.css /usr/share/nginx/html/styles.css
COPY apps/web/app.js /usr/share/nginx/html/app.js
COPY apps/web/account.js /usr/share/nginx/html/account.js
COPY apps/web/catalogo.json /usr/share/nginx/html/catalogo.json
COPY apps/web/experiencias.json /usr/share/nginx/html/experiencias.json
COPY apps/web/experience.js /usr/share/nginx/html/experience.js
COPY apps/web/coragem-demo.js /usr/share/nginx/html/coragem-demo.js
COPY apps/web/pilot-demo.js /usr/share/nginx/html/pilot-demo.js
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
