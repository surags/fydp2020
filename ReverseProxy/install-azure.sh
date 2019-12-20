apt-get update && apt-get install -y\
        uwsgi-plugin-python3 \
        python3 \
        python3-dev

apt-get install -y build-essential \
		libc-dev \
		vim \
		dos2unix \
		libssl-dev \
		libffi-dev \
		iptables

apt-get install -y uwsgi-plugin-python

apt-get install -y python3-pip

python3 -m pip install --no-cache-dir -r requirements.txt

apt-get install -y curl \
  && curl -sL https://deb.nodesource.com/setup_9.x | bash - \
  && apt-get install -y nodejs \
  && curl -L https://www.npmjs.com/install.sh | sh

apt-get install -y libnss3-dev
apt-get install -y unzip