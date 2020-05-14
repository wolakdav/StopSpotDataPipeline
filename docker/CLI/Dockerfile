FROM python:3.7.7
RUN python -m pip install \
        pipenv \
        parse \
        realpython-reader \
        pandas \
        sqlalchemy \
        psycopg2
WORKDIR "/pipeline"
CMD python3 main.py --daily