

import tools.vulmap.run as vulmap_run
import tools.read_scan_vuls_ret as read_vuls
ports = [8080,7001]
for port in ports:
    vulmap_run.start("192.168.79.128", str(port))
ret=read_vuls.read_data()

