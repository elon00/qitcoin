@echo off
title Qitcoin Localhost Node & Explorer
echo Starting Qitcoin (QTC) Localhost Node on port 8080...
echo Web Explorer: http://localhost:8080
echo RPC Endpoint: http://localhost:8080/rpc
echo.
python localhost_node/server.py 8080
pause
