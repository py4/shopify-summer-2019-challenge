FROM python:3.6

RUN mkdir /marketplace

WORKDIR /marketplace

COPY . /marketplace

RUN chmod +x /marketplace/entrypoint.sh

RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["/marketplace/entrypoint.sh"]
