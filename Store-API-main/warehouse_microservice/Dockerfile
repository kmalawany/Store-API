FROM python:3.9
LABEL author="Karim Malawany"
WORKDIR /code1
COPY ./requirements.txt /code1/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code1/requirements.txt
COPY ./app /code1/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]