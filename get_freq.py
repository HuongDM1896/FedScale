from expetator.leverages import dvfs
#import subprocess

#subprocess.run(["bash","/home/hdomai/.local/lib/python3.10/site-packages/expetator/leverages/dvfs_pct.sh", "init"], check=True)
frequencies, pcts = dvfs.get_dvfs_values()

print("Cpu freq available (min, max, delta):", frequencies)
f=list(frequencies)
print("List", f)
print("4 freqquencies for testing", f[0], f[len(f)//3], f[len(f)*2//3], f[-1]) 