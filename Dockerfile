# Docker image for the trie index service
#

FROM python:2-onbuild
RUN pip install -r requirements.txt
EXPOSE 34567
CMD [ "python", "./src/app.py" ]
