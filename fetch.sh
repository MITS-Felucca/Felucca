#!/bin/sh

if [ ! -d "/var/lib/Felucca" ]; then
    sudo git clone https://github.com/MITS-Felucca/Felucca.git /var/lib/Felucca
else
    sudo git pull -C /var/lib/Felucca
fi


