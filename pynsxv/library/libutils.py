#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2015 VMware, Inc. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions
# of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

__author__ = 'yfauser'

from pyVim.connect import SmartConnect
from pyVmomi import vim
import ssl


VIM_TYPES = {'datacenter': [vim.Datacenter],
             'dvs_name': [vim.dvs.VmwareDistributedVirtualSwitch],
             'datastore_name': [vim.Datastore],
             'resourcepool_name': [vim.ResourcePool],
             'host': [vim.HostSystem]}


def get_scope(client_session, transport_zone_name):
    """
    :param client_session: An instance of an NsxClient Session
    :param transport_zone_name: The Name of the Scope (Transport Zone)
    :return: A tuple, with the first item being the scope id as string of the first Scope found with the right name
             and the second item being a dictionary of the scope parameters as return by the NSX API
    """
    try:
        vdn_scopes = client_session.read('vdnScopes', 'read')['body']
        vdn_scope_list = client_session.normalize_list_return(vdn_scopes['vdnScopes'])
        vdn_scope = [scope['vdnScope'] for scope in vdn_scope_list
                     if scope['vdnScope']['name'] == transport_zone_name][0]
    except KeyError:
        return None, None

    return vdn_scope['objectId'], vdn_scope

def get_logical_switch(client_session, logical_switch_name):
    """
    :param client_session: An instance of an NsxClient Session
    :param logical_switch_name: The name of the logical switch searched
    :return: A tuple, with the first item being the logical switch id as string of the first Scope found with the
             right name and the second item being a dictionary of the logical parameters as return by the NSX API
    """
    all_lswitches = client_session.read_all_pages('logicalSwitchesGlobal', 'read')
    try:
        logical_switch_params = [scope for scope in all_lswitches if scope['name'] == logical_switch_name][0]
        logical_switch_id = logical_switch_params['objectId']
    except IndexError:
        return None, None

    return logical_switch_id, logical_switch_params


def get_mo_by_name(content, searchedname, vim_type):
    mo_dict = get_all_objs(content, vim_type)
    for object in mo_dict:
        if object.name == searchedname:
            return object
    return None


def get_all_objs(content, vimtype):
    obj = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for managed_object_ref in container.view:
        obj.update({managed_object_ref: managed_object_ref.name})
    container.Destroy
    return obj


def connect_to_vc(vchost, user, pwd):
    # Disabling SSL certificate verification
    if hasattr(ssl, 'SSLContext'):
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
    else:
        context = None
    if context:
        service_instance = SmartConnect(host=vchost, user=user, pwd=pwd, sslContext=context)
    else:
        service_instance = SmartConnect(host=vchost, user=user, pwd=pwd)

    return service_instance.RetrieveContent()
