import SquidWeb

server = SquidWeb.Website("localhost",80)
server.add_subdomain("/home","test.html")
server.add_subdomain("/calculator","Calculator.html")
server.add_subdomain("/calculator2","Area_per_calc.html")
server.start_server()

"""
# A simpler way for adding subdomains
import SquidWeb
server = SquidWeb.Website("192.168.0.88",80)
server.use_all_in_dir()
server.start_server()
"""
