set /p IP=<ip.txt
start cmd /k ssh -i ec2.pem ubuntu@%IP%
