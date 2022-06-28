set /p IP=<ip.txt
scp -i ec2.pem -r ubuntu@%IP%:~/burgl-discord-bot/python-scripts/status.log ../
