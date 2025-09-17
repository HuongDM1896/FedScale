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
    - filter_less: 21                       # Remove clients w/ less than 21 samples
    - num_loaders: 2
    - local_steps: 2
    - learning_rate: 0.05
    - batch_size: 5
    - test_bsz: 5
    - use_cuda: False
    - save_checkpoint: False
```
6. Run inside fedscale env: 
```bash
fedscale driver submit benchmark/configs/femnist/conf.yml
```
7. Note: also can run outside fedscale, the command to run mannual from outside of fedscale env is:
```bash
bash -i -c 'source ~/.bashrc && conda activate fedscale && cd ~/FedScale && fedscale driver submit benchmark/configs/femnist/conf.yml'
```

