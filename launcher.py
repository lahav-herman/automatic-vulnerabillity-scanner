import subprocess as sp
from termcolor import colored
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
'''
This is a bug bounty automation tool made by AdmiraLahav
It's purpose it to automate and remove the human (me) from the loop;
It is tiering (?) to always check what to do and check if the last command finished to start the next
It is not optimized or efficient, but it is mine so I am happy - 
- also I know everyhting in the code and if something breaks or I want to change something I understand it
'''

'''
                    +--------------------------+
                    |    DEFINING VARIABLES    |
                    +--------------------------+
'''
RESET = "\033[0m"
#colored("","blue") == \033[38;5;4m
#colored("","light_blue") == \033[38;5;12m
inf = "\033[38;5;40m";
INF = fr"[{inf}INF{RESET}]";
err = "\033[38;5;196m";
ERR = fr"[{err}ERR{RESET}]";
wrn = "\033[38;5;220m";
#can change 220 to 226
WRN = fr"[{wrn}WRN{RESET}]";

domain_name = input(f"Domain name: ");
#input domain name
target_dir = f"{domain_name}_BB";
log_f = f"./{target_dir}/LOG_FILE.txt";
subfinder_f = f"./{target_dir}/subfinder_subdomains.txt";
dnsx_f = f"./{target_dir}/dnsx_alive.txt";
naabu_f = f"./{target_dir}/naabu_ports.txt";
httpx_f = f"./{target_dir}/httpx_respond.txt";
katana_f = f"./{target_dir}/katana_crawl.txt";
nuclei_f = f"./{target_dir}/nuclei_final.txt";

time_now = datetime.now(ZoneInfo('Etc/GMT-2'));

log_stage = 0;
log_stages = ["Preperation","subfinder","dnsx","httpx","katana","nuclei","Finish"];

current_stage = log_stages[log_stage];
rate_limit = 50;

all_tools = [
    ("subfinder", f"subfinder -rl {rate_limit} -d {domain_name} -all > {subfinder_f}", subfinder_f),
    ("dnsx", f"dnsx -rl {rate_limit} -l {subfinder_f} -silent > {dnsx_f}", dnsx_f),
    #("naabu", f"naabu -rate {rate_limit} -l {dnsx_f} -top-ports 1000 -silent > {naabu_f}", naabu_f),
    ("httpx", f"httpx -rl {rate_limit} -l {dnsx_f} -ports 8080,80,443 -silent > {httpx_f}", httpx_f),
    ("katana", f"katana -rl {rate_limit} -list {httpx_f} -depth 5 -silent > {katana_f}", katana_f),
    ("nuclei", f"nuclei -rl {rate_limit} -l {katana_f} -severity low,medium,high,critical > {nuclei_f}", nuclei_f)
]
'''
                    +-------------------------------+
                    |    DEFINING DEBUG FUCTIONS    |
                    +-------------------------------+
'''
def WrongDomain():
    print(f"{ERR} Wrong domain entered {ERR}");
    return

def InvalidAnswer():
    print(f"{WRN} Invalid Answer {WRN}");

def MissingOutputFile():
    print(f"{ERR} Missing output file of last command {ERR}");
    print(f"{INF} Current stage: {current_stage} {INF}");
'''
                    +-------------------------------+
                    |    DEFINING TOOL FUNCTIONS    |
                    +-------------------------------+
'''
def CheckOutputFile(file_path):
    path = Path(file_path);

    if not path.exists():
        MissingOutputFile();
        print(f"{ERR} File does not exist: {file_path} {ERR}");
        exit();

    if path.stat().st_size ==0:
        print(f"{WRN} Output file is empty {file_path} {WRN}");
        exit();

    print(f"{INF} Output verified: {file_path}");

def UpdateCurrentStage():
    global log_stage,log_stages,current_stage;
    if log_stage < len(log_stages)-1:
        log_stage+=1;
        current_stage=log_stages[log_stage];

def Log():
    time_now = datetime.now(ZoneInfo('Etc/GMT-2'));
    info = f"[{time_now}] Starting stage: [{current_stage}]\n";
    UpdateCurrentStage();
    sp.run(f"echo '{info}' >> {log_f}" ,shell=True);

def Preperation():
    sp.run(f"mkdir -p {target_dir}",shell=True);
    sp.run(f"echo 'LOG' > {log_f}",shell=True);
    Log();
'''
                    +---------------------+
                    |    START PROGRAM    |
                    +---------------------+
'''
print(f"'{colored(f"{domain_name}","light_blue")}' is the domain");

check = input(f"Is that correct? {colored("[y/n]","light_blue")} ");

while check!="y" or check!="n":
    if check == "y":
        check = True;
        break;
    elif check == "n":
        WrongDomain();
        break;
    else:
        InvalidAnswer();
        check = input(f"Is that correct? {colored("[y/n]","light_blue")}");

if check==True:
    Preperation();
    for stage,tool,outfile in all_tools:
        Log()
        print(f"{INF} Running {stage} {INF}")
        sp.run(tool,shell=True)
        CheckOutputFile(outfile)
