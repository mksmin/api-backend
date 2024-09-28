FROM python

WORKDIR /api_registration_for_atomlab

COPY requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]