import expetator.experiment as experiment
from expetator.monitors import Mojitos
import time 

class FedScale:
    def __init__(self, params=["fedscale"]):
        self.names = {"fedscale"}
        self.params = params

    def build(self, executor):
        return {"fedscale": self.params}

    def run(self, bench, param, executor):
        before = time.time()
        #cmd = f"bash -c 'source ~/.bashrc && conda activate fedscale && cd ~/FedScale && fedscale driver submit benchmark/configs/femnist/conf_g5k.yml'"
        cmd = f"bash -c 'source ~/.bashrc && conda activate fedscale && cd ~/FedScale && python docker/driver.py submit benchmark/configs/femnist/conf_g5k.yml'"
        #cmd = f"bash -c 'source ~/.bashrc && conda activate fedscale && cd ~/FedScale && sleep 5 && fedscale driver submit benchm'"
        executor.local(cmd)
        return time.time() - before, "fedscale"

if __name__ == "__main__":
    experiment.run_experiment(
            "/tmp/fedscale_exp",
            [FedScale()],
            leverages= [],
            monitors= [Mojitos(sensor_set={'user', 'rxp'})],
            times=1
            )
