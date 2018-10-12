#!/usr/bin/env bash

ssh -nNT -o StrictHostKeyChecking=no admin@13.126.155.192 -i /home/tanmoy/awslinux.pem -R 9000:localhost:22
