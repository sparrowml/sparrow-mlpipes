pip install -r requirements-dev.txt
mkdir -p /home/${USER}/.ssh
sudo cp -r /home/${USER}/ssh/. /home/${USER}/.ssh
sudo chown -R ${USER} /home/${USER}/.ssh
sudo chown -R ${USER} .git
