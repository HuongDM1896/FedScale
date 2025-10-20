Even it made me almost crazy but I still need to write it. To avoid some one will get the same stuck as me (or for myself in the future when I totally forget all the steps to fix 1000000 conflicts).
1. Git clone
```bash
git clone git@github.com:HuongDM1896/FedScale.git
```
2. Install anaconda
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc
. ~/.bashrc
```
3. Add alias fedscale
```bash
FEDSCALE_HOME=$(pwd)
echo export FEDSCALE_HOME=$(pwd) >> ~/.bashrc 
echo alias fedscale=\'bash $FEDSCALE_HOME/fedscale.sh\' >> ~/.bashrc 
conda init bash
. ~/.bashrc
```
4. Create conda env
```bash
cd FedScale
conda activate fedscale
pip install -e .
pip install --upgrade pip setuptools wheel
conda install python=3.8.20 numba=0.58.1 tensorboard=2.13.0 -c conda-forge
pip install \
    torch==2.4.1 \
    torchvision==0.19.1 \
    tensorflow==2.12.0 \
    transformers==4.46.3 \
    scipy==1.10.1 \
    matplotlib==3.7.5 \
    overrides==7.7.0 \
    pandas==2.0.3 \
    PyYAML==6.0.2 \
    soxr==0.3.7 \
    grpcio==1.70.0 \
    gym \
    pillow==10.4.0 \
    sentencepiece==0.2.0 \
    h5py==3.11.0 \
    librosa==0.11.0 \
    soundfile==0.13.1 \
    kubernetes \
    wandb \
    psutil \
    tqdm \
    scikit-learn \
    requests
```
5. Check the config in benchmark/configs/femnist/*
```yaml
# Configuration file of FAR training experiment                                                
# ========== Cluster configuration ==========
# ip address of the parameter server (need 1 GPUprocess) 
ps_ip: 172.16.66.6
worker_ips:
    - 172.16.66.7:[1]
    - 172.16.66.8:[1]
exp_path: $FEDSCALE_HOME/fedscale/cloud
# Entry function of executor and aggregator under $exp_path
executor_entry: execution/executor.py

aggregator_entry: aggregation/aggregator.py

auth:
    ssh_user: ""
    # ssh_private_key: ~/.ssh/id_ed25519
    ssh_private_key: ~/.ssh/id_rsa

# cmd to run before we can indeed run FAR (in order)
setup_commands:
   - source ~/.bashrc && conda activate fedscale && cd $FEDSCALE_HOME

  #- source $HOME/miniconda3/bin/activate fedscale

# ========== Additional job configuration ========== 
# Default parameters are specified in config_parser.py, wherein more description of the parameter can be found

job_conf: 
    - job_name: femnist_2                   # Generate logs under this folder: log_path/job_name/time_stamp
    - log_path: $FEDSCALE_HOME/benchmark # Path of log files
    - num_participants: 2                  # Number of participants per round, we use K=100 in our paper, large K will be much slower
    - data_set: femnist                     # Dataset: openImg, google_speech, stackoverflow
    - data_dir: $FEDSCALE_HOME/benchmark/dataset/data/femnist    # Path of the dataset
    - data_map_file: $FEDSCALE_HOME/benchmark/dataset/data/femnist/client_data_mapping/train.csv              # Allocation of data to each client, turn to iid setting if not provided
    - device_conf_file: $FEDSCALE_HOME/benchmark/dataset/data/device_info/client_device_capacity     # Path of the client trace
    - device_avail_file: $FEDSCALE_HOME/benchmark/dataset/data/device_info/client_behave_trace
    - model: resnet18             # NOTE: Please refer to our model zoo README and use models for these small image (e.g., 32x32x3) inputs
#    - model_zoo: fedscale-torch-zoo
    - eval_interval: 1                     # How many rounds to run a testing on the testing set
    - rounds: 3                          # Number of rounds to run this training. We use 1000 in our paper, while it may converge w/ ~400 rounds
    - filter_less: 21                       # Remove clients w/ less than 21 samples - set =0 if clients less than 21.
    - num_loaders: 2
    - local_steps: 2
    - learning_rate: 0.05
    - batch_size: 5
    - test_bsz: 5
    - use_cuda: False
    - save_checkpoint: False
```
6. Run inside fedscale env: 

dataset: 
```bash
fedscale dataset download femnist
```

```bash
fedscale driver submit benchmark/configs/femnist/conf.yml
```
7. Note: also can run outside fedscale, the command to run mannual from outside of fedscale env is:
```bash
bash -i -c 'source ~/.bashrc && conda activate fedscale && cd ~/FedScale && fedscale driver submit benchmark/configs/femnist/conf.yml'
```

Kill all the process in all nodes before re start if crash.

After use expetator got blocking, cmd stop: 

bash -i -c 'source ~/.bashrc && conda activate fedscale && cd ~/FedScale && fedscale driver stop femnist_expe'

mdo@gros-43:~/FedScale$ ps aux | grep mdo | grep fedscale
mdo        24188  0.0  0.0   2480   516 pts/0    T    15:31   0:00 /bin/sh -c bash -i -c 'source ~/.bashrc && conda activate fedscale && cd ~/FedScale && fedscale driver submit benchmark/configs/femnist/conf_g5k.yml'
mdo        24189  0.0  0.0   7028  3216 pts/0    T    15:31   0:00 bash -i -c source ~/.bashrc && conda activate fedscale && cd ~/FedScale && fedscale driver submit benchmark/configs/femnist/conf_g5k.yml

Find solution:
1.
use cmd = f"bash -i -c 'source ~/.bashrc && conda activate fedscale && cd ~/FedScale && fedscale driver submit {param} &'" " not work

2. reduce number of client in setting

problem of connection.
check in main: mdo@gros-58:~/FedScale$ lsof -i:29500
COMMAND     PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
pt_main_t 10817  mdo    7u  IPv6  41674      0t0  TCP *:29500 (LISTEN)
pt_main_t 10817  mdo    8u  IPv6  77902      0t0  TCP gros-58.nancy.grid5000.fr:29500->gros-90.nancy.grid5000.fr:39492 (ESTABLISHED)
pt_main_t 10817  mdo    9u  IPv6  77904      0t0  TCP gros-58.nancy.grid5000.fr:29500->gros-94.nancy.grid5000.fr:56806 (ESTABLISHED) --> ok


pip3 install git+https://gitlab.irit.fr/sepia-pub/expetator.git@master
upgrade expetator as repo



NOOO: it is container docker. but can run in native: follow command: 

```bash
ssh hdomai@172.16.66.88 source /home/mdo/anaconda3/bin/activate fedscale && python /home/mdo/FedScale/fedscale/cloud/aggregation/aggregator.py  --time_stamp 1014_111318 --ps_ip 172.16.66.88 --job_name cifar_10_g5k --log_path /home/mdo/FedScale/benchmark --num_participants 3 --data_set cifar10 --data_dir /home/mdo/FedScale/benchmark/dataset/data/ --model custom_cnn --model_zoo fedscale-torch-zoo --eval_interval 1 --rounds 2 --filter_less 0 --num_loaders 2 --local_steps 1 --learning_rate 0.01 --batch_size 32 --test_bsz 32 --use_cuda False --save_checkpoint False --this_rank=0 --num_executors=3 --executor_configs=172.16.66.90:[1]=172.16.66.91:[1]=172.16.66.98:[1]
```

```bash
ssh 172.16.66.90 source ~/.bashrc && conda activate fedscale && cd /home/mdo/FedScale && python /home/mdo/FedScale/fedscale/cloud/aggregation/aggregator.py --time_stamp 1014_130501 --ps_ip 172.16.66.90 --job_name test --log_path /home/mdo/FedScale/benchmark --num_participants 3 --data_set cifar10 --data_dir /home/mdo/FedScale/benchmark/dataset/data/ --model custom_cnn --model_zoo fedscale-torch-zoo --eval_interval 1 --rounds 2 --filter_less 0 --num_loaders 2 --local_steps 1 --learning_rate 0.01 --batch_size 32 --test_bsz 32 --use_cuda False --save_checkpoint False --this_rank=0 --num_executors=3 --executor_configs=172.16.66.98:[1]=172.16.66.91:[1]=172.16.66.99:[1]
```


and also client:

```bash
bash -c source ~/.bashrc && conda activate fedscale && cd /home/mdo/FedScale &&   python /home/mdo/FedScale/fedscale/cloud/execution/executor.py  --time_stamp 1014_130133 --ps_ip 172.16.66.90 --job_name test --log_path /home/mdo/FedScale/benchmark --num_participants 3 --data_set cifar10 --data_dir /home/mdo/FedScale/benchmark/dataset/data/ --model custom_cnn --model_zoo fedscale-torch-zoo --eval_interval 1 --rounds 2 --filter_less 0 --num_loaders 2 --local_steps 1 --learning_rate 0.01 --batch_size 32 --test_bsz 32 --use_cuda False --save_checkpoint False --this_rank=2 --num_executors=3 --cuda_device=cuda:0
```


SERVER: 172.16.66.90 (run tai server k can ssh)

source ~/.bashrc && conda activate fedscale && cd /home/mdo/FedScale && python /home/mdo/FedScale/fedscale/cloud/aggregation/aggregator.py --time_stamp 1014_131400 --ps_ip 172.16.66.90 --job_name test --log_path /home/mdo/FedScale/benchmark --num_participants 3 --data_set cifar10 --data_dir /home/mdo/FedScale/benchmark/dataset/data/ --model custom_cnn --model_zoo fedscale-torch-zoo --eval_interval 1 --rounds 2 --filter_less 0 --num_loaders 2 --local_steps 1 --learning_rate 0.01 --batch_size 32 --test_bsz 32 --use_cuda False --save_checkpoint False --this_rank=0 --num_executors=3 --executor_configs=172.16.66.98:[1]=172.16.66.91:[1]=172.16.66.99:[1]


CLIENT 1: 172.16.66.98

ssh 172.16.66.98 source ~/.bashrc && conda activate fedscale && cd /home/mdo/FedScale && python /home/mdo/FedScale/fedscale/cloud/execution/executor.py  --time_stamp 1014_131400 --ps_ip 172.16.66.90 --job_name test --log_path /home/mdo/FedScale/benchmark --num_participants 3 --data_set cifar10 --data_dir /home/mdo/FedScale/benchmark/dataset/data/ --model custom_cnn --model_zoo fedscale-torch-zoo --eval_interval 1 --rounds 2 --filter_less 0 --num_loaders 2 --local_steps 1 --learning_rate 0.01 --batch_size 32 --test_bsz 32 --use_cuda False --save_checkpoint False --this_rank=1 --num_executors=3 --cuda_device=cuda:0

CLIENT 2: 172.16.66.91

ssh 172.16.66.91 source ~/.bashrc && conda activate fedscale && cd /home/mdo/FedScale && python /home/mdo/FedScale/fedscale/cloud/execution/executor.py  --time_stamp 1014_131400 --ps_ip 172.16.66.90 --job_name test --log_path /home/mdo/FedScale/benchmark --num_participants 3 --data_set cifar10 --data_dir /home/mdo/FedScale/benchmark/dataset/data/ --model custom_cnn --model_zoo fedscale-torch-zoo --eval_interval 1 --rounds 2 --filter_less 0 --num_loaders 2 --local_steps 1 --learning_rate 0.01 --batch_size 32 --test_bsz 32 --use_cuda False --save_checkpoint False --this_rank=2 --num_executors=3 --cuda_device=cuda:0


CLIENT 2: 172.16.66.99

ssh 172.16.66.99 source ~/.bashrc && conda activate fedscale && cd /home/mdo/FedScale && python /home/mdo/FedScale/fedscale/cloud/execution/executor.py  --time_stamp 1014_131400 --ps_ip 172.16.66.90 --job_name test --log_path /home/mdo/FedScale/benchmark --num_participants 3 --data_set cifar10 --data_dir /home/mdo/FedScale/benchmark/dataset/data/ --model custom_cnn --model_zoo fedscale-torch-zoo --eval_interval 1 --rounds 2 --filter_less 0 --num_loaders 2 --local_steps 1 --learning_rate 0.01 --batch_size 32 --test_bsz 32 --use_cuda False --save_checkpoint False --this_rank=3 --num_executors=3 --cuda_device=cuda:0