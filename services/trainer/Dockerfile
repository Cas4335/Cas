FROM python:3.12-slim

# This trainer scaffold is NOT required for v1 runtime.
# It is disabled by default (profile: training).
# It has no network access to the production stack.

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "trainer.main"]
