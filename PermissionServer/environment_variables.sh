export CLIENT_IP=$(ip route show default | awk '/default/ {print $3}')
