import os

os.system("ps -eo pid,ppid,cmd > fedscale_running_temp")

# Đọc tất cả process
procs = {}
children = {}
with open("fedscale_running_temp") as f:
    for line in f.readlines()[1:]:
        pid, ppid, *cmd = line.strip().split()
        pid, ppid = int(pid), int(ppid)
        cmdline = " ".join(cmd)
        procs[pid] = (ppid, cmdline)
        children.setdefault(ppid, []).append(pid)

def print_tree(pid, indent=0):
    if pid not in procs:
        return
    ppid, cmd = procs[pid]
    print(" " * indent + f"{pid} {cmd}")
    for c in children.get(pid, []):
        print_tree(c, indent + 4)

# In tất cả process grep theo job_name
with open("fedscale_running_temp") as f:
    for line in f.readlines():
        if "job_name=fedscale_job" in line:
            pid = int(line.split()[1])
            print_tree(pid)

os.remove("fedscale_running_temp")
