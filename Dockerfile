FROM ckaaj/superthon:slim-buster

#clonning repo 
RUN git clone https://github.com/cKaaj/superthon.git /root/superthon
#working directory 
WORKDIR /root/superthon

# Install requirements
RUN pip3 install --no-cache-dir -r requirements.txt

ENV PATH="/home/superthon/bin:$PATH"

CMD ["python3","-m","superthon"]
