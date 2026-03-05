FROM python:3.10-slim  

WORKDIR /flask-api
RUN mkdir /flask-api/preprocessing
ADD preprocessing /flask-api/preprocessing/

COPY /backend/ /flask-api/*
COPY requirements.txt  /flask-api/
RUN pip3 install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN cd /flask-api/preprocessing && python3 main.py
RUN mv /flask-api/preprocessing/variants.db /flask-api/
RUN cd /flask-api/

EXPOSE 8080 

CMD ["gunicorn", "application:app", "-b", "0.0.0.0:8080", "-w", "4"]
LABEL RUN='podman run -d -p 8080:8080 --name bodlexicon  ${IMAGE}' 
