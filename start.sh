# stop script on error
set -e

printf "\n Polling Bravia TV to dt topic"
python3 pollBraviaToTelemetry.py -e 192.168.1.101 -r certs/AVRGGRoot.pem -c certs/Bravia_cert_pem_file -k certs/Bravia_private_key_pem_file -n "Denon" --topic "dt/avr/family-room/bravia" --tvIP 192.168.1.194 --psk 0000
