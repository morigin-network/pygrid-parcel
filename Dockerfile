FROM openmined/grid-domain

RUN mkdir /avgplan
WORKDIR /avgplan
RUN git clone https://github.com/OpenMined/PyGrid.git

WORKDIR /avgplan/PyGrid/apps/domain/src/main
COPY avg.py .

ENTRYPOINT ["python", "avg.py"]
