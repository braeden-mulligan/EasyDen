echo "Please provide LAN credentials and server socket address to build project."

if [[ $1 = "-b" || $1 = "--bogus" ]]; then
	ssid="x"
	pass="y"
	addr="z"
	port="a"
else
	read -p "WiFi SSID > " ssid
	read -p "WiFi password > " pass
	read -p "Socket Address > " addr
	read -p "Socket Port > " port
fi

if [[ $1 = "-f" || $2 = "-f" ]]; then
	make full WIFI_DEFINES="-DWIFI_SSID=\\\"$ssid\\\" -DWIFI_PASS=\\\"$pass\\\" -DSOCKET_ADDR=\\\"$addr\\\" -DSOCKET_PORT=\\\"$port\\\""
else
	make all WIFI_DEFINES="-DWIFI_SSID=\\\"$ssid\\\" -DWIFI_PASS=\\\"$pass\\\" -DSOCKET_ADDR=\\\"$addr\\\" -DSOCKET_PORT=\\\"$port\\\""
fi
