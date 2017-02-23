FROM continuumio/miniconda3

ENTRYPOINT []
CMD [ "/bin/bash" ]

#set proxy
ARG http_proxy
ENV http_proxy $http_proxy
ENV https_proxy $http_proxy

# Remove (large file sizes) MKL optimizations.
RUN conda install -y nomkl
RUN conda install -y numpy scipy scikit-learn matplotlib pandas

ADD ./requirements.txt /tmp/requirements.txt
RUN pip install -qr /tmp/requirements.txt

# Add our code
ADD ./karura /opt/karura/
WORKDIR /opt/karura/

CMD python /opt/karura/bot/run.py
