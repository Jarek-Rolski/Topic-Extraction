# pull official base image
FROM jupyter/datascience-notebook

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN rm ./requirements.txt

RUN python -m spacy download en_core_web_sm

# set working directory
WORKDIR /usr/src/app




