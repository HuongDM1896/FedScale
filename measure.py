# python measure.py -m Net -e Exp -r 5

import expetator.experiment as experiment
from expetator.monitors import Mojitos, kwollect
from expetator.leverages import Dvfs
import time, os, argparse
import platform

# Set up argument parser
parser = argparse.ArgumentParser(description="Run a benchmark experiment")
parser.add_argument("-m", "--model", type=str, required=True, help="Model name")
parser.add_argument("-r", "--repeat", type=int, default=1, required=True, help="Number of repetitions (e.g., 2, the experiment will run twice)")
parser.add_argument("-e", "--exp", type=str, required=True, help="Experiment name")
args = parser.parse_args()
OUTPUT = "Log"
MODEL = args.model
EXP = args.exp

def get_g5k_target_metric(cluster_name=None):
    if cluster_name is None:
        cluster_name = platform.node().split('-')[0]

    if cluster_name in ['grimani', 'grimoire', 'grimoire',
                        'gros', 'parasilo', 'paravance']:
        return 'pdu_outlet_power_watt'
    if cluster_name in ['troll', 'yeti', 'gemini', 'neowise', 'servan', 'sirius', 'paradoxe',
                        'orion', 'pyxis', 'sagittaire', 'taurus', 'nova', 'chirop', 'engelbourg','fleckenstein']:
        
        return 'wattmetre_power_watt'
    return 'bmc_node_power_watt'

kwollect.get_g5k_target_metric = get_g5k_target_metric

class fedscale:
    def __init__(self, params=["fedscale"]):
        self.names = {"fedscale"}
        self.params = params

    def build(self, executor):
        return {"fedscale": self.params}

    def run(self, bench, param, executor):
        before = time.time()
        cmd = f"python run_fedscale.py -e {EXP} -m {MODEL}"
        executor.local(cmd)
        return time.time() - before, "fedscale"

# Log directory
if MODEL == "custom_cnn":
    name = "Net"
elif MODEL == "resnet18_cus":
    name = "ResNet18"
elif MODEL == "mobilenetv2_cus":
    name = "MobileNetV2"

current_dir = os.getcwd() #Fedscale
log_dir = os.path.join(current_dir, f"{OUTPUT}") #Fedscale/Log
exp_log_dir = os.path.join(log_dir, f"Fedscale_{EXP}", f"Fedscale_{name}", "Expetator")
os.makedirs(exp_log_dir, exist_ok=True) #Fedscale/Log/Fedscale_exp/fedscale_model/Expetator_

if __name__ == "__main__":
    experiment.run_experiment(
            exp_log_dir,
            [fedscale()],
            leverages= [Dvfs(frequencies=[1200000,1500000,1800000,2100000])],
            monitors= [Mojitos(sensor_set={'user', 'rxp', 'dram0'}),
                kwollect.Power(metric=kwollect.get_g5k_target_metric())],
            times=args.repeat
            )
