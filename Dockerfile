FROM python:3.9-slim 

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["python3","/app/src/file_recognition/exec_file.py"] 
