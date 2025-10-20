import subprocess
import time

# ----- CONFIG -----
TIME_STAMP = "1014_131400"
PS_IP = "172.16.66.55"
JOB_NAME = "test"
DATASET = "cifar10"
MODEL = "custom_cnn"
MODEL_ZOO = "fedscale-torch-zoo"
NUM_EXECUTORS = 3
NUM_PARTICIPANTS = 3
ROUNDS = 3
BASE_DIR = "/home/mdo/FedScale"
DATA_DIR = f"{BASE_DIR}/benchmark/dataset/data/"
LOG_PATH = f"{BASE_DIR}/benchmark"
SAVE = f"{BASE_DIR}/ici"

# ----- NODES -----
SERVER = "172.16.66.55"
CLIENTS = [
    "172.16.66.65",
    "172.16.66.75",
    "172.16.66.82",
]

# ----- COMMON PARAMS -----
COMMON_ARGS = (
    f"--time_stamp {TIME_STAMP} "
    f"--ps_ip {PS_IP} "
    f"--job_name {JOB_NAME} "
    f"--log_path {LOG_PATH} "
    f"--num_participants {NUM_PARTICIPANTS} "
    f"--data_set {DATASET} "
    f"--data_dir {DATA_DIR} "
    f"--model {MODEL} "
    f"--model_zoo {MODEL_ZOO} "
    f"--eval_interval 1 "
    f"--rounds {ROUNDS} "
    f"--filter_less 0 "
    f"--num_loaders 2 "
    f"--local_steps 500 "
    f"--learning_rate 0.01 "
    f"--batch_size 32 "
    f"--test_bsz 32 "
    f"--use_cuda False "
    f"--save_checkpoint False "
)

# ----- AGGREGATOR -----
aggregator_cmd = (
    f"python {BASE_DIR}/fedscale/cloud/aggregation/aggregator.py "
    + COMMON_ARGS
    + f"--this_rank=0 --num_executors={NUM_EXECUTORS} "
    + f"--executor_configs={CLIENTS[0]}:[1]={CLIENTS[1]}:[1]={CLIENTS[2]}:[1]"
)

server_log = f"{SAVE}/server"

print(f"[SERVER] Starting aggregator on {SERVER} ...")

# server_process = subprocess.Popen(
#     f"bash -c 'source ~/.bashrc >/dev/null 2>&1 && conda activate fedscale && "
#     f"cd {BASE_DIR} && {aggregator_cmd} > {server_log} 2>&1'",
#     shell=True,
# )

server_process = subprocess.Popen(
    f"ssh -T {SERVER} \"bash -c 'source ~/.bashrc >/dev/null 2>&1 && conda activate fedscale && "
    f"cd {BASE_DIR} && {aggregator_cmd} > {server_log} 2>&1'\"",
    shell=True,
)

# time.sleep(5)  # Give aggregator time to start

# ----- EXECUTORS -----
processes = []
for i, client in enumerate(CLIENTS, start=1):
    executor_cmd = (
        f"python {BASE_DIR}/fedscale/cloud/execution/executor.py "
        + COMMON_ARGS
        + f"--this_rank={i} --num_executors={NUM_EXECUTORS} --cuda_device=cuda:0"
    )
    
    ssh_cmd = (
        f"ssh -T {client} \"bash -c 'source ~/.bashrc >/dev/null 2>&1 && conda activate fedscale && "
        f"cd {BASE_DIR} && {executor_cmd} > {SAVE}/client_{i} 2>&1 &'\""
    )

    print(f"[CLIENT {i}] Starting on {client} ...")
    p = subprocess.Popen(ssh_cmd, shell=True)
    processes.append(p)
    # time.sleep(2)

# ----- MONITOR -----
print("\nAll nodes launched. Aggregator and executors are running.")
print(f"Logs: {SAVE}/server and {SAVE}/client_*")

# Wait for server process to finish
server_process.wait()

# Ensure SSH commands complete (though they run in background)
for p in processes:
    p.wait()

print("\nFinish.")
