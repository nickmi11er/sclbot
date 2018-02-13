#!/bin/bash

echo 'Trying to bootstrap the bot'

filename="$1"

if [ -z "$filename" ]; then
  echo 'Enter encerypted filename with settings: '
  read file
  filename="$file"
fi
if [ ! -f "$filename" ]; then
  echo 'Lol. This is not a real file. Better luck another time'
  exit 0
fi
printf "Trying to decrypt file $filename\n"
if [ ! -d "assets" ]; then
  mkdir assets
fi
openssl enc -d -aes-256-cbc -in "$filename" -out assets/settings.dat > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo 'Successfully encrypted settings file. Moving on'
else
  echo 'Cannot decrypt file. Check password and try again'
  exit 1
fi
git log --pretty=format:'%H' -n 1 > assets/rev.hash

