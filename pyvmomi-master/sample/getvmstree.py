#!/usr/bin/python

# Based on getallvms.py

"""
Python program for listing the vms on an ESX / vCenter host in tree like view
"""

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

def GetArgs():
   """
   Supports the command-line arguments listed below.
   """
   parser = argparse.ArgumentParser(description='Process args for retrieving all the Virtual Machines')
   parser.add_argument('-s', '--host', required=True, action='store', help='Remote host to connect to')
   parser.add_argument('-o', '--port', default=443,   action='store', help='Port to connect on')
   parser.add_argument('-u', '--user', required=True, action='store', help='User name to use when connecting to host')
   parser.add_argument('-p', '--password', required=True, action='store', help='Password to use when connecting to host')
   args = parser.parse_args()
   return args

def printLevel(text, level):

   # indent print, with tree levels
   n = 0
   while n <= level:
      print "\b    ",
      n += 1
   print text

def iterateTree(item, level):
   """
   Iterate through VM Folders and VirtualApp objects,
   Then print out VM information
   """
   nlevel = level + 1

   # Check for VM folders
   if type(item) == pyVmomi.types.vim.Folder:
      printLevel("`-Folder Name : %s" % (item.name), level)
      # Iterate through objects in that Folder
      for cItem in item.childEntity:
         iterateTree(cItem, nlevel)

   # Check for vApps
   elif type(item) == pyVmomi.types.vim.VirtualApp:
      printLevel("`-vApp Name : %s" % (item.name), level)
      # Iterate through VM in that vApp
      for cItem in item.vm:
         iterateTree(cItem, nlevel)

   else:
      PrintVmInfo(item, level)


def PrintVmInfo(vm, level):
   """
   Print information for a particular virtual machine.
   """

   summary = vm.summary
   printLevel("| VM Name    : %s" % summary.config.name, level)
   printLevel("| Path       : %s" % summary.config.vmPathName, level)
   printLevel("| Guest OS   : %s" % summary.config.guestFullName, level)
   annotation = summary.config.annotation
   if annotation != None and annotation != "":
      for line in annotation.split("\n"):
         for shortline in textwrap.wrap(line, 80):
            printLevel("| Annotation : %s" % shortline, level)

   printLevel("| Status     : %s" % summary.runtime.powerState, level)
   if summary.guest != None:
      ip = summary.guest.ipAddress
      if ip != None and ip != "":
         printLevel("| IP         : %s" % ip, level)
   if summary.runtime.question != None:
      printLevel("| Question         : %s" % summary.runtime.question.text, level)
   printLevel("--", level)

def getvApp_withVMList(item, vappname):
       vApp = []
       if type(item) == pyVmomi.types.vim.VirtualApp and item.name == vappname:
          print("find vapp")
          for cItem in item.vm:
              vmItem = {cItem.summary.config.name: cItem.summary.guest.ipAddress}
              vApp.append(vmItem)

       return vApp




def main():
   """
   Simple command-line program for listing the virtual machines on a system.
   """

   args = GetArgs()
   try:
      si = None
      try:
         si = SmartConnect(
            host  = args.host,
            user  = args.user,
            pwd   = args.password,
            port  = int(args.port)
         )
      except IOError, e:
        pass
      if not si:
         print "Could not connect to the specified host using specified username and password"
         return -1

      atexit.register(Disconnect, si)

      content = si.RetrieveContent()
      datacenter = content.rootFolder.childEntity[0]
      vmFolder = datacenter.vmFolder
      vmFolderList = vmFolder.childEntity


      for curItem in vmFolderList:
            print(getvApp_withVMList(curItem,"vApp_migration_auto"))

   except vmodl.MethodFault, e:
      print "Caught vmodl fault : " + e.msg
      return -1
   except Exception, e:
      print "Caught exception : " + str(e)
      return -1

   return 0

# Start program
if __name__ == "__main__":
   main()