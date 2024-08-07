FROM python:3
LABEL authors="gmolino"

ENV TOKEN 5096860506:AAGLlu1Ftd2FyVBbSjaLGz37zpqfR85bCcU
ENV CHATID 591331731
ENV LOOP_TIME 150
ENV HOST2CHECK reinvent.dyndns.org

WORKDIR /app
COPY requirements .
RUN pip install -r requirements

COPY watchdog.py .
CMD ["python", "watchdog.py"]
