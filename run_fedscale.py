'''
Docstring for try_it:
Remove the useless args (also removed these args in aggregator. corres current aggregator.py no wandb)
'''
# python run_finish.py -m Net -e Exp

import subprocess
import time
import os
from datetime import datetime
import argparse
import socket

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# ----- NODES -----
with open("hostfile") as f:
    hosts = [l.strip() for l in f if l.strip()]

ips = [socket.gethostbyname(h) for h in hosts]
SERVER = ips[0]
CLIENTS = ips[1:]

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", type=str, default="custom_cnn")
parser.add_argument("-e", "--exp", type=str, required=True, help="Experiment name")
args = parser.parse_args()

# ----- CONFIG -----
PS_IP = SERVER
JOB_NAME = "test"
DATASET = "cifar10"
MODEL = args.model
MODEL_ZOO = "fedscale-torch-zoo"
NUM_PARTICIPANTS = 3
NUM_EXECUTORS = 3
ROUNDS = 11
EXP = args.exp
OUTPUT = "Log"

# ----- NEW BASE DIR FOR FEDSCALE -----
BASE_DIR = os.getcwd() # Fedscale "/home/mdo/FedScale"
DATA_DIR = f"{BASE_DIR}/benchmark/dataset/data/cifar"
LOG_PATH = f"{BASE_DIR}/benchmark"
log_dir = f"{BASE_DIR}/{OUTPUT}" #Fedscale/Log/

if MODEL == "custom_cnn":
    name = "Net"
elif MODEL == "resnet18_cus":
    name = "ResNet18"
elif MODEL == "mobilenetv2_cus":
    name = "MobileNetV2"

fedscale_log_dir = os.path.join(log_dir, f"Fedscale_{EXP}", f"Fedscale_{name}")
SAVE = f"{fedscale_log_dir}/Fedscale_{timestamp}"
os.makedirs(SAVE, exist_ok=True)

# ----- COMMON PARAMS -----
COMMON_ARGS = (
    f"--ps_ip {PS_IP} "
    f"--job_name {JOB_NAME} "
    f"--log_path {LOG_PATH} "
    f"--num_participants {NUM_PARTICIPANTS} "
    f"--num_executors {NUM_EXECUTORS} "
    f"--data_set {DATASET} "
    f"--data_dir {DATA_DIR} "
    f"--model {MODEL} "
    f"--model_zoo {MODEL_ZOO} "
    f"--eval_interval 1 "
    f"--rounds {ROUNDS} "
    f"--filter_less 0 "
    f"--num_loaders 0 "
    f"--local_steps 512 "
    f"--learning_rate 0.01 "
    f"--batch_size 32 "
    f"--test_bsz 32 "
    f"--use_cuda False "
    f"--save_checkpoint False "
    f"--sample_mode local "
)

# ----- AGGREGATOR -----
aggregator_cmd = (
    f"python {BASE_DIR}/fedscale/cloud/aggregation/aggregator.py "
    + COMMON_ARGS
    + f"--this_rank=0 "
    + f"--executor_configs={CLIENTS[0]}:[1]={CLIENTS[1]}:[1]={CLIENTS[2]}:[1]"
)

server_log = f"{SAVE}/server"

print(f"[SERVER] Starting aggregator on {SERVER} ...")

server_process = subprocess.Popen(
    f"ssh -T {SERVER} \"bash -c 'source fedscale-venv/bin/activate && "
    f"cd {BASE_DIR} && {aggregator_cmd} > {server_log} 2>&1'\"",
    shell=True,
)

time.sleep(5)  # Give aggregator time to start

# ----- EXECUTORS -----
processes = []
for i, client in enumerate(CLIENTS, start=1):
    executor_cmd = (
        f"python {BASE_DIR}/fedscale/cloud/execution/executor.py "
        + COMMON_ARGS
        + f"--this_rank={i}"
    )
    
    ssh_cmd = (
        f"ssh -T {client} \"bash -c 'source fedscale-venv/bin/activate && "
        f"cd {BASE_DIR} && {executor_cmd} > {SAVE}/client_{i} 2>&1'\""
    )

    print(f"[CLIENT {i}] Starting on {client} ...")
    p = subprocess.Popen(ssh_cmd, shell=True)
    processes.append(p)
    time.sleep(3)

# ----- MONITOR -----
print("\nAll nodes launched. Aggregator and executors are running.")
print(f"Logs: {SAVE}/server and {SAVE}/client_*")

# Wait for server process to finish
server_process.wait()

# Ensure SSH commands complete (though they run in background)
for p in processes:
    p.wait()

print("\nFinish.")
