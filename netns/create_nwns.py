#!/usr/bin/python

import os
import subprocess
import optparse
import sys
import atexit

connectors = []
namespaces = []
success = False

def output_of(cmd, env_arg={}):

    env_dict = dict(os.environ)
    env_dict.update(env_arg)

    if type(cmd) == list:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, \
                stderr=subprocess.PIPE, env=env_dict, close_fds=True)
    else:
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, \
                stderr=subprocess.PIPE, env=env_dict, close_fds=True)

    return_str = ""
    for line in iter(proc.stdout.readline, ''):
        return_str += line
    proc.stdout.close()
    proc.stderr.close()
    proc.wait()
    return proc.returncode, return_str.strip()

def run_and_log(cmd, env_arg={}):
    from multiprocessing.dummy import Pool as ThreadPool

    if type(cmd) == list:
        cmd_str = " "
        for tk in cmd:
            cmd_str += " %s" % tk
    else:
        cmd_str = cmd

    print "E: " + cmd_str

    env_dict = dict(os.environ)
    env_dict.update(env_arg)

    if type(cmd) == list:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, \
                stderr=subprocess.PIPE, env=env_dict, close_fds=True)
    else:
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, \
                stderr=subprocess.PIPE, env=env_dict, close_fds=True)

    def handle_output(line):
        print line

    def stream_readline(stream):
        for line in iter(stream.readline, ''):
            handle_output(line.strip())

    pool = ThreadPool(2)
    pool.map(stream_readline, [proc.stdout, proc.stderr])
    pool.close()
    pool.join()
    proc.stdout.close()
    proc.stderr.close()
    proc.wait()
    return proc.returncode


def exec_command(cmd_str):
    rc = run_and_log(cmd_str)
    if rc != 0:
        print "CMD %s failed" %cmd_str
        exit(1)
 
def cleanup_at_exit():

    if success:
        return
    print "Cleanup on premature exit"

    for ns in namespaces:
        cmd = "ip netns del %s" %ns
        run_and_log(cmd)

    for link in connectors:
        cmd = "ovs-vsctl del-port %s" %link
        run_and_log(cmd)
        cmd = "ip link delete %s" %link
        run_and_log(cmd)

def check_in_default_namespace():
    pid = os.getpid()
    rc, rstr = output_of("ip netns identify %s" %pid)
    if len(rstr) > 0:
        print "Currently in %s namespace, change to default" %rstr
        exit(1)

if __name__ == "__main__":

    if os.geteuid() != 0:
        print "Run %s as root" % sys.argv[0]
        exit(1)

    check_in_default_namespace()

    program_name = "%prog"
    usage_str = "%s [options]" %program_name
    parser = optparse.OptionParser(usage=usage_str)
    parser.add_option("-c", "--net-name", dest="name",\
        help="Context or Network Name")
    parser.add_option("-n", "--num-host", dest="count",\
        type="int", help="No. of hosts in the network")
    parser.add_option("-v", "--vlan", dest="vlan",\
        type="int", help="VLAN to use in OVS")
    parser.add_option("-b", "--bridge", dest="bridge",\
        help="OVS Bridge to connect to")
    parser.add_option("-d", "--dhcp-host-ip", dest="dhcp_host",\
        help="Static IP for the DHCP host")
    parser.add_option("-m", "--mask", dest="netmask",\
        help="Subnet Mask")
    parser.add_option("-r", "--range", dest="dhcp_range",\
        help="DHCP Range")

    (options, args) = parser.parse_args()

    optdict = vars(options)
    for key, val in optdict.items():
        if not val:
            print "Option %s is missing" %key
            parser.print_help()
            exit(1)

    #Validate whether the ovs bridge exists
    rc = run_and_log("ovs-ofctl show %s" %options.bridge)
    if rc != 0:
        print "No bridge found %s" %options.bridge
        exit(1)

    atexit.register(cleanup_at_exit)

    #Create the DHCP namespace first
    print "Create the DHCP namespace first"
    dhcp_ns = "dhcp-%s" %options.name
    cmd = "ip netns add %s" %dhcp_ns
    exec_command(cmd)

    namespaces.append(dhcp_ns)

    #Create the veth pairs
    print "Create the veth pairs"
    ns_iface = "e0-%s" %dhcp_ns
    switch_iface = "v0-%s" %dhcp_ns
    cmd = "ip link add %s type veth peer name %s" %(ns_iface, switch_iface)
    exec_command(cmd)

    connectors.append(switch_iface)

    iface_up_template = "ip link set dev %s up"
    ns_exec_template = "ip netns exec %s %s" 

    #Attach one end of veth pair to the dhcp nw_namespace, bring it UP
    print "Attach one end of veth pair to the dhcp nw_namespace, bring it UP"
    cmd = "ip link set %s netns %s" %(ns_iface, dhcp_ns)
    exec_command(cmd)
    iface_up = iface_up_template %ns_iface
    cmd = ns_exec_template %(dhcp_ns, iface_up)
    exec_command(cmd)
    #Also bring up the loopback iface
    print "Also bring up the loopback iface"
    temp_iface = "lo"
    iface_up = iface_up_template %temp_iface
    cmd = ns_exec_template %(dhcp_ns, iface_up)
    exec_command(cmd)
    #Now assign the IP address to the DHCP interface
    print "Now assign the IP address to the DHCP interface"
    assign_ip_cmd = "ip address add %s/%s dev %s"\
                  %(options.dhcp_host, options.netmask, ns_iface)
    cmd = ns_exec_template %(dhcp_ns, assign_ip_cmd)
    exec_command(cmd)
    #Start the DHCP server on the dhcp nw_namespace
    print "Start the DHCP server on the dhcp nw_namespace"
    dnsmasq_cmd = "dnsmasq --interface=%s --dhcp-range=%s,%s"\
                   %(ns_iface, options.dhcp_range, options.netmask)
    cmd = ns_exec_template %(dhcp_ns, dnsmasq_cmd)
    exec_command(cmd)

    #Attach the other end of veth pair to the OVS bridge and bring it UP
    print "Attach the other end of veth pair to the OVS bridge and bring it UP"
    cmd = "ovs-vsctl add-port %s %s" %(options.bridge, switch_iface)
    exec_command(cmd)
    #Tag this port with the VLAN
    print "Tag this port with the VLAN"
    cmd = "ovs-vsctl set port %s tag=%s" %(switch_iface, options.vlan)
    exec_command(cmd)
    cmd = iface_up_template %switch_iface
    exec_command(cmd)

    for hindex in range(0, options.count):
        host_ns = "host%s-%s" %(hindex, options.name)
        print "Creating Host NS %s" %host_ns
        cmd = "ip netns add %s" %host_ns
        exec_command(cmd)

        namespaces.append(host_ns)

        #Create the veth pairs
        print "Create the veth pairs for host %s" %host_ns
        ns_iface = "e0-%s" %host_ns
        switch_iface = "v0-%s" %host_ns
        cmd = "ip link add %s type veth peer name %s" %(ns_iface, switch_iface)
        exec_command(cmd)

        connectors.append(switch_iface)
        print "Attach one end of veth pair to the host %s bring it UP" %host_ns
        cmd = "ip link set %s netns %s" %(ns_iface, host_ns)
        exec_command(cmd)
        iface_up = iface_up_template %ns_iface
        cmd = ns_exec_template %(host_ns, iface_up)
        exec_command(cmd)
        print "Also bring up the loopback iface"
        temp_iface = "lo"
        iface_up = iface_up_template %temp_iface
        cmd = ns_exec_template %(host_ns, iface_up)
        exec_command(cmd)

        print "Attach the other end of veth pair to the OVS bridge and bring it UP"
        cmd = "ovs-vsctl add-port %s %s" %(options.bridge, switch_iface)
        exec_command(cmd)
        print "Tag this port with the VLAN"
        cmd = "ovs-vsctl set port %s tag=%s" %(switch_iface, options.vlan)
        exec_command(cmd)
        cmd = iface_up_template %switch_iface
        exec_command(cmd)

        print "Calling dhclient on interface :%s" %ns_iface
        dhclient_cmd = "dhclient %s" %ns_iface
        cmd = ns_exec_template %(host_ns, dhclient_cmd)
        exec_command(cmd)

    success = True 
    print "SUCCESS"
    exit(0)
