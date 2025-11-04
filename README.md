<img width="537" height="128" alt="ascii-art-text" src="https://github.com/user-attachments/assets/31cdcfd1-d3c0-4216-ac41-fce93b1eb5b7" />

MITMProxy2GQL is a proxy that captures GQL queries and parses them into a schema


## How to Install **MITMProxy2GQL**
1. Clone the Repository
```bash
git clone https://github.com/j4xx3n/MITMProxy2GQL.git

cd MITMProxy2GQL
chmod +x *.py *.sh
```
2. Run the installer and start the enviroment
```bash
./installer.sh

source venv/bin/activate 
```
3. Run MITMProxy2GQL and add the SSL certificate to chromium
```bash
./proxy.py
```
- Add `~/.mitmproxy/mitmproxy-ca-cert.cer` to the allowed certificates


## How to Use
1. Start the enviroment and run MITMProxy2GQL
```bash
source venv/bin/activate
./proxy.py
```
2. Enter the target domain running graphql
```bash
Enter Domain to Proxy: example.com
```
3. Browse the website and use all features
4. Press enter to stop the proxy and parse the results
