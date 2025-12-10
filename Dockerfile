FROM python:3.13.9

WORKDIR /usr/src/PatentWriterBot

COPY . .


RUN pip install -r requirements.txt

CMD ["streamlit", "run", "ui/app.py", "--server.address=0.0.0.0"]