FROM python:3.10.7

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080
CMD ["python", "main.py"]
