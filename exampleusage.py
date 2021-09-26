import SquidWeb

server = SquidWeb.Website("localhost",80)
server.add_subdomain("/home","test.html")
server.add_subdomain("/calculator","Calculator.html")
server.add_subdomain("/calculator2","Area_per_calc.html")
server.start_server()
