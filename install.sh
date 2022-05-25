
#!/bin/bash
apt-get -y update
apt-get -y install --no-install-recommends wget unzip curl git

python3 -m pip install --upgrade pip
python3 -m pip install -e ".[testing]"

wget -q -O /tmp/tfenv.tar.gz https://github.com/tfutils/tfenv/archive/refs/tags/v${TFENV_VERSION}.tar.gz
tar -zxf /tmp/tfenv.tar.gz -C /tmp
mkdir /usr/local/.tfenv && mv /tmp/tfenv-${TFENV_VERSION}/* /usr/local/.tfenv && chmod u+x /usr/local/.tfenv/bin/tfenv
echo "/usr/local/.tfenv/bin" >> $GITHUB_PATH

chmod u+x /usr/local/bin/*
apt-get clean
rm -rf /var/lib/apt/lists/*
rm -rf /tmp/*