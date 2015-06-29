__author__ = 'amy1'

from optparse import OptionParser, make_option
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vmodl

import pyVmomi
import textwrap
import argparse
import atexit
import sys

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import yaml

import os
import logging

logging.basicConfig(filename=os.path.join(os.getcwd(), 'vsphere.log'), level = logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

def getmyList(vmFolderList):
    for citem in vmFolderList:
        if type(citem) == pyVmomi.types.vim.VirtualApp:
            vapp = []
            for cvm in citem.vm:
                vmitem = {cvm.summary.config.name: cvm.summary.guest.ipAddress}
                vapp.append(vmitem)
            logging.info(citem.name)
            logging.info(vapp)
        elif type(citem) == pyVmomi.types.vim.VirtualMachine:
            vmitem = {citem.summary.config.name: citem.summary.guest.ipAddress}
            logging.info(vmitem)

    return None

def createSnap_vapp(vmFolderList, vappname, snapname):
    for citem in vmFolderList:
        if type(citem) == pyVmomi.types.vim.VirtualApp and citem.name == vappname:
            for cvm in citem.vm:
                cvm.CreateSnapshot_Task(name=snapname, memory=False, quiesce=False)

    return None

def revertSnap_vapp(vmFolderList, vappname, snapname):
    for citem in vmFolderList:
        if type(citem) == pyVmomi.types.vim.VirtualApp and citem.name == vappname:
            for cvm in citem.vm:
                rootsnap = cvm.snapshot.rootSnapshotList
                snap_obj = revert_Snapshot(rootsnap[0], snapname)
                if snap_obj is not None:
                    logging.info("revert snapshot to %s for vm %s"%(snapname, cvm.summary.config.name))

    return None


def revert_Snapshot(snap, snapname):
    if snap.name == snapname:
        snap_obj = snap.snapshot
        snap_obj.RevertToSnapshot_Task(suppressPowerOn=False)
        logging.info("revert snapshot to %s"%(snapname))
    elif (len(snap.childSnapshotList)!=0):
        for child in snap.childSnapshotList:
            revert_Snapshot(child, snapname)
    else:
        return None

def removeSnap_vapp(vmFolderList, vappname, snapname):
    for citem in vmFolderList:
        if type(citem) == pyVmomi.types.vim.VirtualApp and citem.name == vappname:
            for cvm in citem.vm:
                rootsnap = cvm.snapshot.rootSnapshotList
                snap_obj = remove_Snapshot(rootsnap[0], snapname)
                if snap_obj is not None:
                    logging.info("remove snapshot %s for vm %s"%(snapname, cvm.summary.config.name))
    return None


def remove_Snapshot(snap, snapname):

    if snap.name == snapname:
        snap_obj = snap.snapshot
        snap_obj.RemoveSnapshot_Task(removeChildren=False)
    elif (len(snap.childSnapshotList)!=0):
        for child in snap.childSnapshotList:
            remove_Snapshot(child, snapname)
    else:
        return None


def main():

    with open("params.yaml", 'r') as stream:
        params = yaml.load(stream)

    operation = params['operation']
    vappname = params['vappname']
    snapname = str(params['snapname'])

    si = SmartConnect(
            host  = params['host'],
            user  = params['user'],
            pwd   = params['password'],
            port  = int(params['port']),
            )

    atexit.register(Disconnect, si)

    content = si.RetrieveContent()
    datacenter = content.rootFolder.childEntity[0]
    vmFolder = datacenter.vmFolder
    vmFolderList = vmFolder.childEntity

    if operation == 'list':
        getmyList(vmFolderList)
    elif operation == 'revert':
        revertSnap_vapp(vmFolderList, vappname, snapname)
    elif operation == 'create':
        createSnap_vapp(vmFolderList, vappname, snapname)
    elif operation == 'remove':
        createSnap_vapp(vmFolderList, vappname, snapname)
    else:
        logging.info("operation %s is not supported"%(operation))


# Start program
if __name__ == "__main__":
   main()
