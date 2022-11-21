FROM python:3.8

ADD app.py .

COPY wms wms/
COPY stl_generator stl_generator/

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install libgl1 -y

CMD ["python", "./app.py"]

