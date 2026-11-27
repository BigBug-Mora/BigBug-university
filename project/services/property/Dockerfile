FROM python:3.14.6-slim-bookworm

WORKDIR /app

COPY shared/requirements-auth.txt project/shared/
COPY services/property/requirements.txt project/services/property/
RUN python -m pip install --no-cache-dir -r project/services/property/requirements.txt

COPY shared/cognito.py shared/service_auth.py project/shared/
COPY services/property/app.py services/property/actor.py services/property/engagement.py project/services/property/

USER 10001:10001

CMD ["python", "-m", "uvicorn", "project.services.property.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
