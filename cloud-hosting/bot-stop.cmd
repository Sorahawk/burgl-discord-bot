set /p IP=<ip.txt
ssh -i ec2.pem ubuntu@%IP% "sudo systemctl stop burgl-bot.service"
