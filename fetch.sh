#!/bin/sh

if [ ! -d "/var/tmp/Felucca" ]; then
    git clone https://github.com/MITS-Felucca/Felucca.git /var/tmp/Felucca
else
    git -C /var/tmp/Felucca pull
fi

cp ./env/mongodb.sh /tmp/Felucca/mongodb.sh
chmod 0744 /tmp/Felucca/mongodb.sh
cp ./felucca.sh /tmp/Felucca/felucca.sh
chmod 0744 /tmp/Felucca/felucca.sh


