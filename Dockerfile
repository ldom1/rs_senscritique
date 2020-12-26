FROM python
MAINTAINER Louis Giron

RUN mkdir models
RUN mkdir models/artefact
RUN mkdir models/metadata
ENV GLOBAL_DATA_PATH=data/
ENV MODEL_PATH=models/artefact/artefact.joblib
ENV METADATA_PATH=models/metadata/meta_data.json

COPY data/ /data/
COPY rssenscritique/ /rssenscritique/
COPY setup.py ./setup.py

RUN pip install --upgrade pip
RUN pip install -e .
RUN python3 rssenscritique/recommended_system/train.py

