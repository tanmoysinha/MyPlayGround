#!/usr/bin/python

import os
import subprocess
import optparse
import sys

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
        help="Context or Network Name to cleanup")
    parser.add_option("-b", "--bridge", dest="bridge",\
        help="OVS Bridge to cleanup")

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
        print "No bridge found %s err:%s" %options.bridge
        exit(1)

    cmd = "ip netns list  | grep %s | tr -s ' ' | tr '\n' ';'" %options.name
    rc = run_and_log(cmd)
    if  rc != 0:
        print "Namespace %s lookup error" %options.name
        exit(1)

    rc, rstr = output_of(cmd)
    ns_list = rstr.split(';')

    for ns in ns_list:
        if len(ns) > 0:
            print "Deleting namespace %s" %ns
            cmd = "ip netns del %s" %ns
            run_and_log(cmd)

    cmd = "ovs-vsctl list-ports %s | grep %s | tr -s ' ' | tr '\n' ';'" \
           %(options.bridge, options.name)
    rc = run_and_log(cmd)
    if  rc != 0:
        print "Veth ports lookup error for network:%s" %options.name
        exit(1)

    rc, rstr = output_of(cmd)
    veth_list = rstr.split(';')

    for link in veth_list:
        if len(link) > 0:
            print "Deleting virtual link %s" %link
            cmd = "ovs-vsctl del-port %s" %link
            run_and_log(cmd)
            cmd = "ip link delete %s" %link
            run_and_log(cmd)
