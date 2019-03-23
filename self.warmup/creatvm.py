import libvirt
import os

DOMAIN_XML_TEMPLATE = """ 
<domain type='kvm'>
    <name>tanmoy-test</name> 
    <memory unit='KiB'>8388608</memory> 
    <vcpu placement='static'>20</vcpu> 
    <features> 
        <pae/> 
        <acpi/> 
        <apic/> 
    </features> 
    <os> 
        <type arch='x86_64' machine='pc-i440fx-2.1'>hvm</type> 
        <boot dev='hd'/> 
    </os>
    <cpu mode='custom' match='exact'>
      <model fallback='allow'>Haswell-noTSX</model>
      <vendor>Intel</vendor>
      <feature policy='require' name='vme'/>
      <feature policy='require' name='ss'/>
      <feature policy='require' name='ht'/>
      <feature policy='require' name='vmx'/>
      <feature policy='require' name='osxsave'/>
      <feature policy='require' name='f16c'/>
      <feature policy='require' name='rdrand'/>
      <feature policy='require' name='pdpe1gb'/>
      <feature policy='require' name='abm'/>
      <feature policy='require' name='invtsc'/>
      <feature policy='disable' name='tsc-deadline'/>
    </cpu>
    <devices> 
        <emulator>/usr/bin/kvm</emulator> 
        <input type='tablet' bus='usb'/>
        <input type='mouse' bus='ps2'/> 
        <input type='keyboard' bus='ps2'/> 
        <disk type='file' device='disk'> 
            <driver name='qemu' type='qcow2'/> 
            <source file='/var/lib/libvirt/images/tanmoy-debug/guest-disk.qcow2'/> 
            <target dev='hda' bus='ide'/> 
        </disk> 
        <interface type='network'>
            <source network='cache-br-net'/>
        </interface>
        <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'> 
            <listen type='address' address='0.0.0.0'/> 
        </graphics> 
    </devices> 
</domain>
"""

if __name__ == "__main__":

    conn = None
    try:
        conn = libvirt.open("qemu:///system")
    except libvirt.libvirtError as le:
        print "Unable to open connection err:%s" %le.get_error_message()
        exit(1)


    try:
        guest = conn.defineXML(DOMAIN_XML_TEMPLATE) 
    except libvirt.libvirtError as le:
        print "Unable to define guest err:%s" %le.get_error_message()
        conn.close()
        exit(1)

    try:
        rc = guest.create()
    except libvirt.libvirtError as le:
        print "Unable to create guest err:%s" %le.get_error_message()
        try:                                                                                      
            guest.destroy()                                                                       
        except libvirt.libvirtError:                                                              
            pass                                                
        try:                                                                                      
            guest.undefine()                                                                      
        except libvirt.libvirtError:                                                              
            pass
        conn.close()
        exit(1)

    print "Guest created"
    exit(0)
