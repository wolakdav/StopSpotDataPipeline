FROM python:3.7.7
COPY . /project
RUN python -m pip install \
        pipenv \
        parse \
        realpython-reader \
        pandas \
        sqlalchemy \
        psycopg2 \
        Flask
WORKDIR /project/ui
CMD ["python", "app.py"]