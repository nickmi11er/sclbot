# -*- coding: utf-8 -*-
import SocketServer
import signal, sys, os
import subprocess, shlex
from enum import Enum
#===================================
#   stop
#   restart
#   start
#   status: RUNNING, STOPPED, STARTING
#===================================
NO_PID = 0

bot_exec_p = ""
running_pid = NO_PID

remove_empt_elems = lambda x: x != '' and x != ' ' 

class COMMANDS(Enum):
    START = 0,
    STOP = 1,
    RESTART = 2,
    STATUS = 3,
    KILL = 4

def parse_cmd(cmd):
    if cmd == "start":
        return COMMANDS.START
    elif cmd == "stop":
        return COMMANDS.STOP
    elif cmd == "restart":
        return COMMANDS.RESTART
    elif cmd == "status":
        return COMMANDS.STATUS
    elif cmd == "suicide":
        return COMMANDS.KILL

def get_pid_from_cmd():
    p = "pgrep -f src/bot.py"
    r = subprocess.Popen(shlex.split(p), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.stdout

def parse_pid_output(output):
    return " ".join(line.strip() for line in output)

def get_pid_from_output(output):
    if output == '':
        return 0, []
    else:
        temp = output.split()
        if len(temp) > 1:
            #Несколько цифр (возможно старые процессы)
            temp = [int(x.strip()) for x in temp]
            max_pid = max(temp) # Максимальный PID - самый новый процесс
            return max_pid, temp
        else:
            # Одна цифра
            return int(output), [] 

#Собственный сигнал и сигнальный обработчик в bot.py
def kill_procs_by_pid(procs=[], exclude=0):
    for pid in procs:
        if pid != exclude:
            os.kill(pid, signal.SIGUSR1)
    return exclude

def get_bot_pid():
    output = get_pid_from_cmd()
    output = parse_pid_output(output)
    max_pid, procs = get_pid_from_output(output)
    max_pid = kill_procs_by_pid(procs=procs, exclude=max_pid)
    return max_pid


def start_bot_loc():
    global running_pid
    if running_pid == NO_PID or get_bot_pid() == NO_PID:
        running_pid = start_bot().pid
        return ("[CLI] Bot started with pid = {}".format(running_pid), True)
    else:
        return ("[CLI] Bot already running", False)

def stop_bot():
    global running_pid
    if running_pid == NO_PID:
        return ("[CLI] Bot is not running...", False)
    else:
        r = get_bot_pid()
        running_pid = max(r, running_pid)
        os.kill(running_pid, signal.SIGUSR1)
        return ("[CLI] OK", True)

def get_bot_hash():
    try:
        with open('assets/rev.hash') as f:
            h = ''
            for line in f:
                h+=line.strip()
            if h != '':
                return h
    except FileNotFoundError:
        return 'None'

def do(cmd):
    ans = ""
    status = False
    command = parse_cmd(cmd)
    if command == COMMANDS.START:
        ans, status = start_bot_loc()
    elif command == COMMANDS.STOP:
        ans, status = stop_bot()
    elif command == COMMANDS.RESTART:
        ans, status = stop_bot()
        if status:
            ans, status = start_bot_loc()
        else:
            return ans
    elif command == COMMANDS.RESTART:
        global running_pid
        if running_pid == 0 or get_bot_pid() == 0:
            ans = "[CLI] Stopped."
        else:
            ans = "[CLI] Running. ID = {}.".format(running_pid)
            ans += '\nRunning version = ' + get_bot_hash()
    elif command == COMMANDS.KILL:
        print "[CLI] AMA killing myself"
        stop_bot()
    return ans

class MySocketHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print "[CLI] Connect from {}. Command = {}".format(self.client_address[0], self.data)
        ans = do(self.data)
        if ans == "SUI":
            sys.exit(0)
        self.request.sendall(ans)


def server(proc):
    print "[CLI] Bot start with pid = {}".format(proc.pid)
    global running_pid
    running_pid = proc.pid
    host, port = '0.0.0.0', 1488
    server = SocketServer.TCPServer((host, port), MySocketHandler)
    print "[CLI] Server runnning in {}:{}".format(host, port)
    server.serve_forever()

def append_path(left, right):
    left_l = filter(remove_empt_elems, left.split('/'))
    right_l = filter(remove_empt_elems, right.split('/'))
    for p in right_l:
        if p == '..' and len(left_l) > 1:
            left_l.pop()
        else:
            left_l.append(p)
    return ("/" if left[0] == "/" else "") +  "/".join(left_l)

def start_bot():
    botenv = os.getenv('BOT_ENV', "!")
    if botenv == "!":
        print "[CLI] Sorry. Problem with python env"
        os._exit(1)
    python_ex = append_path(botenv, "bin/python/ /")
    p_exec_path = append_path(os.getcwd(), python_ex)
    prod = "" if (os.getenv('MODE', 'prod') == 'prod') else '-B'
    p_exec_path += " " + prod + " src/bot.py"
    args = shlex.split(p_exec_path)
    print "[CLI] Starting bot from cli...."
    #spawning
    proc = subprocess.Popen(args)
    return proc


#   Предполагаем, что этот скрипт запустился от start.sh
if __name__ == "__main__":
    bot_proc = start_bot()
    get_bot_pid()
    server(bot_proc)


