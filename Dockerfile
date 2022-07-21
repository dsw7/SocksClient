FROM debian

RUN apt-get update && apt-get install -y cmake g++ git make

EXPOSE 8080

CMD git clone https://github.com/dsw7/ChristmasSocks.git \
 && cd ChristmasSocks \
 && make release \
 && ./ChristmasSocks/bin/socks --bind-ip 0.0.0.0 --master 172.17.0.1
