# environment construction
FROM ubuntu:20.04
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update
RUN apt-get install -y vim
RUN apt-get install -y net-tools
RUN apt-get install -y iputils-ping
RUN apt-get install -y curl
RUN apt-get install -y wget
RUN apt-get install -y openssh-server
RUN apt-get install -y openssh-client
RUN apt-get install -y git
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-setuptools
RUN apt-get install -y python3-venv
RUN apt-get install -y python3-wheel

# project deployment
COPY . /app
WORKDIR /app
RUN python3 -m pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com

# run the project
RUN chmod +x /app/run.sh
