import json
from pathlib import Path

path = Path.cwd()
data_path = path.parent / "python_system_tools/data.json"
with open(file=data_path) as f:
    data = json.load(f)
ip_address = data["proxy_address"]
user_name = data["user"]
password = data['password']
nqn = 'nqn.2016-06.io.spdk:cnode0'
spdk_port = 5260
nvme_port = '4420'
sma_port = 8080
sock = '/home/berta/IPDK_workspace/SHARE/vm_socket'