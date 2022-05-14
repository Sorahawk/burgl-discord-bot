set /p IP=<ip.txt
scp -i ec2.pem -r ./transfer-folder/ ubuntu@%IP%:~/
