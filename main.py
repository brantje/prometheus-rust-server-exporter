from pprint import pprint
import websocket
import json
from os import getenv
from prometheus_client import start_http_server, Gauge, REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR, GC_COLLECTOR 
from time import sleep

[REGISTRY.unregister(c) for c in [PROCESS_COLLECTOR, PLATFORM_COLLECTOR, GC_COLLECTOR ]]

DESCRIPTIONS = {
    'collections': '',
    'entitycount': 'Amount of entities',
    'framerate': 'Server side fps',
    'joining': 'Current amout of players joining',
    'maxplayers': 'Max players on server',
    'memory': 'Memort usage',
    'networkin': 'Network in',
    'networkout': 'Network out',
    'players': 'Current amount of players',
    'queued': 'Current amout of players in queue',
    'restarting': 'If the server is restarting or not',
    'uptime': 'Server uptime',
}

STATS = {}

def get_rust_server_info(ip, port, password):
    server_uri = 'ws://{0}:{1}/{2}'.format(ip, port, password)
    command_json = {}
    command_json['Identifier'] = 1
    command_json['Message'] = 'serverinfo'
    command_json['Name'] = 'WebRcon'
    command_json = json.dumps(command_json)
    ws = websocket.WebSocket()

    try:
       ws.connect(server_uri)
       ws.send(command_json)
       response = ws.recv()
       ws.close()
       response = json.loads(response.replace('\n', ''))
       response = json.loads(response['Message'])

       del response['GameTime']
       del response['SaveCreatedTime']
       del response['Hostname']
       del response['Map']

       response = dict((k.lower(), v) for k,v in response.items())

       for k,v in response.items():
            if(k not in STATS):
               STATS[k]  = Gauge('rustserver_'+ k, DESCRIPTIONS.get(k, 'Rust server '+k))
            
            STATS[k].set(v) 

    except Exception as e:
       pprint(e)
       # Inform the user it was a failure to connect. provide Exception string for further diagnostics.
       response = 'Failed to connect. {}'.format(str(e))

if __name__ == '__main__':
    port = getenv('EXPORTER_PORT', 8000)
    start_http_server(port)
    print('Prometheus exporter running at port', port)
    rcon_ip = getenv('RCON_IP', 'localhost')
    rcon_port = getenv('RCON_PORT', 28016)
    rcon_pass = getenv('RCON_PASSWORD')
    while True:
        get_rust_server_info(rcon_ip, rcon_port, rcon_pass)
        sleep(15)

