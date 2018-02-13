#!/bin/bash

env=$1

if [ -z "$env" ] || [ ! -d "$env" ] ; then
  echo 'Provide me virtualenv plz'
  exit 1
fi

echo 'Activating virtualenv'

#source "$env/bin/activate"

if [ ! $? -eq  0 ]; then
  echo 'Something went wrong. Bye'
  exit 1
fi

echo 'Installing requirements from requirements.txt'

"$env/bin/pip" install -r requirements.txt > /dev/null 2>&1

if [ ! $? -eq 0 ]; then
  echo 'pip died. Sry =('
  exit 1
fi

if [ -z "$2" ]; then
  "$env/bin/python" -B src/bot.py & 
else
  "$env/bin/python" src/bot.py &
fi

t_pid=$!

printf "Alright!\nBot is started! (PID = $t_pid)\n"

#deactivate




