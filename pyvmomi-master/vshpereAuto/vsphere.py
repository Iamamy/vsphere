__author__ = 'amy1'

from optparse import OptionParser, make_option
from pyVim.connect import SmartConnect, Disconnect

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

logging.basicConfig(filename=os.path.join(os.getcwd(), 'templates','log.html'), level = logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())


class vsphere():
    def getmyList(self, vmFolderList):
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

    def createSnap_vapp(self, vmFolderList, vappname, snapname):
        for citem in vmFolderList:
            if type(citem) == pyVmomi.types.vim.VirtualApp and citem.name == vappname:
                for cvm in citem.vm:
                    logging.info("create snapshot %s for vm %s"%(snapname, cvm.summary.config.name))
                    cvm.CreateSnapshot_Task(name=snapname, memory=False, quiesce=False)

        return None

    def revertSnap_vapp(self, vmFolderList, vappname, snapname):
        for citem in vmFolderList:
            if type(citem) == pyVmomi.types.vim.VirtualApp and citem.name == vappname:
                for cvm in citem.vm:
                    rootsnap = cvm.snapshot.rootSnapshotList
                    snap_obj = self.revert_Snapshot(rootsnap[0], snapname)
                    if snap_obj is not None:
                        logging.info("revert snapshot to %s for vm %s"%(snapname, cvm.summary.config.name))

        return None


    def revert_Snapshot(self, snap, snapname):
        if snap.name == snapname:
            snap_obj = snap.snapshot
            snap_obj.RevertToSnapshot_Task(suppressPowerOn=False)
            # logging.info("revert snapshot to %s"%(snapname))
            return snap_obj
        elif len(snap.childSnapshotList)!=0:
            for child in snap.childSnapshotList:
                self.revert_Snapshot(child, snapname)
        else:
            return None

    def removeSnap_vapp(self, vmFolderList, vappname, snapname):
        for citem in vmFolderList:
            if type(citem) == pyVmomi.types.vim.VirtualApp and citem.name == vappname:
                for cvm in citem.vm:
                    rootsnap = cvm.snapshot.rootSnapshotList
                    snap_obj = self.remove_Snapshot(rootsnap[0], snapname)
                    if snap_obj is None:
                        logging.info("remove snapshot %s for vm %s"%(snapname, cvm.summary.config.name))
        return None


    def remove_Snapshot(self, snap, snapname):

        if snap.name == snapname:
            snap_obj = snap.snapshot
            snap_obj.RemoveSnapshot_Task(removeChildren=False)
            return snap_obj
        elif (len(snap.childSnapshotList)!=0):
            for child in snap.childSnapshotList:
                self.remove_Snapshot(child, snapname)
        else:
            return snap

    def start_operation(self):
        with open("params.yml", 'r') as stream:
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
            self.getmyList(vmFolderList)
        elif operation == 'revertsnapshot':
            self.revertSnap_vapp(vmFolderList, vappname, snapname)
        elif operation == 'createsnapshot':
            self.createSnap_vapp(vmFolderList, vappname, snapname)
        elif operation == 'deletesnapshot':
            self.removeSnap_vapp(vmFolderList, vappname, snapname)
        else:
            logging.info("operation %s is not supported"%(operation))




