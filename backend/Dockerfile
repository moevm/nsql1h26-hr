FROM python:3.12

WORKDIR /backend

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
