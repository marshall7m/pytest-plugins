
#!/bin/bash
apt-get update
apt-get -y update
apt-get install -y aptitude
aptitude install -y software-properties-common build-essential wget unzip git

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

wget -q -O /tmp/tfenv.tar.gz https://github.com/tfutils/tfenv/archive/refs/tags/v${TFENV_VERSION}.tar.gz
tar -zxf /tmp/tfenv.tar.gz -C /tmp
mkdir /usr/local/.tfenv && mv /tmp/tfenv-${TFENV_VERSION}/* /usr/local/.tfenv && chmod u+x /usr/local/.tfenv/bin/tfenv

chmod u+x /usr/local/bin/*
apk del .build-deps
rm -rf /tmp/*
rm -rf /var/cache/apk/*