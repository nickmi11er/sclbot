#!/bin/bash

env=$1

if [ -z "$env" ] || [ ! -d "$env" ] ; then
  echo 'Provide me virtualenv plz'
  exit 1
fi

echo 'Checking virtualenv'


if [ ! -f "$env/bin/pip" ] || [ ! -f "$env/bin/python" ] ; then
  echo 'This is not virtualenv'
  exit 1
fi

echo 'Checking python version....'

v="$($env/bin/python -V 2>&1)"

if [[ $v != *"2.7."* ]]; then
  echo "Sorry, we need Python 2.7.x"
  exit 1
fi



echo 'Installing requirements from requirements.txt'

"$env/bin/pip" install -r requirements.txt > /dev/null 2>&1

if [ ! $? -eq 0 ]; then
  echo 'pip died. Sry =('
  exit 1
fi

if [[ $2 != "prod" ]]; then
  env MODE='test' "$env/bin/python" -B src/bot.py & 
else
  env MODE='prod' "$env/bin/python" src/bot.py &
fi

t_pid=$!

printf "Alright!\nBot is started! (PID = $t_pid)\n"

#deactivate




