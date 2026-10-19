# Build from the repository root:  docker build -f services/api/Dockerfile .
FROM python:3.12-slim
WORKDIR /srv
COPY services/api/requirements.txt /srv/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
 && useradd -u 10001 -m mentor && mkdir /data && chown mentor /data
COPY services/api/mentor_api /srv/mentor_api
COPY packages/curriculum/curriculum.json /srv/curriculum/curriculum.json
COPY apps/web /srv/web
USER mentor
ENV DATABASE_PATH=/data/mentor.db \
    CURRICULUM_PATH=/srv/curriculum/curriculum.json \
    WEB_DIR=/srv/web
# Client IPs (used for rate limits) come from X-Forwarded-For only when the
# connection originates from FORWARDED_ALLOW_IPS (uvicorn default: 127.0.0.1).
EXPOSE 8000
CMD ["python","-m","uvicorn","mentor_api.app:app","--host","0.0.0.0","--port","8000","--proxy-headers"]
