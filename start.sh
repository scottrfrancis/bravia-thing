# stop script on error
set -e

printf "\n Polling Bravia TV to SHADOW\n"
python3 pollBraviaToShadow.py -e 192.168.1.101 -r certs/AVRGGRoot.pem -c certs/Bravia_cert_pem_file -k certs/Bravia_private_key_pem_file -n "Bravia"  --tvIP 192.168.1.177 --psk 0000
