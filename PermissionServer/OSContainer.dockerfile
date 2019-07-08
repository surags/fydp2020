FROM ubuntu:16.04

## Connection ports for controlling the UI:
# VNC port:5901
# noVNC webport, connect via http://IP:6901/?password=vncpassword

ENV DISPLAY=:1 \
    VNC_PORT=5901

EXPOSE $VNC_PORT

### Envrionment config
ENV HOME=/headless \
    TERM=xterm \
    STARTUPDIR=/dockerstartup \
    INST_SCRIPTS=/headless/install \
    DEBIAN_FRONTEND=noninteractive \
    VNC_COL_DEPTH=24 \
    VNC_RESOLUTION=1024x600 \
    VNC_PW=vncpassword \
    VNC_VIEW_ONLY=false
WORKDIR $HOME

### Add all install scripts for further steps
ADD ./oscontainer/src/common/install/ $INST_SCRIPTS/
ADD ./oscontainer/src/ubuntu/install/ $INST_SCRIPTS/
RUN find $INST_SCRIPTS -name '*.sh' -exec chmod a+x {} +

### Install some common tools
RUN $INST_SCRIPTS/tools.sh
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

#### Install custom fonts
RUN $INST_SCRIPTS/install_custom_fonts.sh

#### Install xvnc-server & noVNC - HTML5 based VNC viewer
RUN $INST_SCRIPTS/tigervnc.sh

#### Install firefox and chrome browser
RUN $INST_SCRIPTS/firefox.sh

#### Install xfce UI
RUN $INST_SCRIPTS/xfce_ui.sh
ADD ./oscontainer/src/common/xfce/ $HOME/

#### configure startup
RUN $INST_SCRIPTS/libnss_wrapper.sh
ADD ./oscontainer/src/common/scripts $STARTUPDIR
RUN $INST_SCRIPTS/set_user_permission.sh $STARTUPDIR $HOME

######## Setup Permissions Server
WORKDIR $STARTUPDIR

RUN apt-get update && apt-get install -y\
        uwsgi-plugin-python3 \
        python3 \
        python3-dev

RUN apt-get install -y build-essential \
		libc-dev \
		vim \
		dos2unix \
		libssl-dev \
		libffi-dev

RUN apt-get install -y uwsgi-plugin-python

COPY . $STARTUPDIR
COPY requirements.txt $STARTUPDIR


RUN apt-get install -y python3-pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt


#USER 1000

ENTRYPOINT ["/dockerstartup/start.sh"]
#docker run --cap-add=NET_ADMIN --name os -v "$(pwd)/src:/dockerstartup/src/" --net mynet -p5901:5901 oscontainer:latest
#chmod -R -x /usr/lib/<app name>