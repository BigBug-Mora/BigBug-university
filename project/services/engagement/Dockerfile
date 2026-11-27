FROM python:3.14.6-slim-bookworm

WORKDIR /app

COPY shared/requirements-auth.txt project/shared/
COPY services/engagement/requirements.txt project/services/engagement/
RUN python -m pip install --no-cache-dir -r project/services/engagement/requirements.txt

COPY shared/cognito.py shared/service_auth.py project/shared/
COPY services/engagement/app.py services/engagement/accounts.py project/services/engagement/

USER 10001:10001

CMD ["python", "-m", "uvicorn", "project.services.engagement.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
