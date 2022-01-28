# run

at first install docker then run mqtt-broker

```bash
docker run -p 8080:8080 -p 1883:1883 hivemq/hivemq4
```

http://localhost:8080/ #hive web

now install requirements

```bash
python3.8 -m virtualenv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt

```

now run central_server

```bash
python central_server.py
```

now run flask-mqtt as local server

```bash
python local_server.py
```

