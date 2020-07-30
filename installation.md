# Automated installation
1. Install ansible
```
sudo apt-get update
sudo apt install -y software-properties-common
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt install -y ansible
```

2. Clone the project
```
git clone https://github.com/MITS-Felucca/Felucca.git
cd Felucca
```

3. Run ansible playbook
```
ansible-playbook env/setup.yml
```

4. Change the ip address in frontend

- change backend ip address from ```'http://54.84.171.25:5000'``` to your backend ip address in ```felucca/frontend/src/environments/environment.prod.ts```

5. Start Felucca
```
./felucca_control.sh start
```

6. Stop Felucca
```
./felucca_control.sh stop
```

# Manually installation
## Requirments
- Python3
- python3-pip
- virtualenv
- nodejs 12
- angalur/cli 10.0.3
- docker latest
- mongodb 4.2

## Python virtual environment requirments
- Flask==1.1.1
- pymongo==3.10.1
- docker==4.2.0
- Sphinx==3.1.2
- sphinx_rtd_theme==0.5.0

## Steps

1. Start mongodb service
```
sudo service mongod start
```

2. Change the ip address in frontend

- change backend ip address from ```'http://54.84.171.25:5000'``` to your backend ip address in ```felucca/frontend/src/environments/environment.prod.ts```


3. Start backend
activate python virtual environment
```
cd felucca/backend
python3 server.py
```

4. Start frontend
```
cd felucca/frontend
ng serve --host=0.0.0.0 --configuration=production --disable-host-check
```
