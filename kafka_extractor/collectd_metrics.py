# -*- coding: utf-8 -*-
#
# custom measurement metric name for each collectd plugin
# the name of the function should match the corresponding plugin name
#

from config import cfg

ping_cfg = cfg["collectd"].get("ping")

def get_metric_name(data):
    # get the corresponding function for the plugin
    func = globals().get(data['plugin'])
    if func is not None:
        metric_name = func(data)
        if metric_name is not None:
            return metric_name

    default_metric_name = "%s___%s___%s___%s" %(
            data['plugin'],
            data['plugin_instance'],
            data['type'],
            data['type_instance'],
        )
    return default_metric_name


def memory(data):
    if data['type'] == 'memory' and data['type_instance'] == 'free':
        return 'memory_free'

def cpu(data):
    if data['type'] == 'percent' and data['type_instance'] == 'active':
        return 'cpu_usage'

def interface(data):
    if data['type'] in ['if_octets', 'if_packets', 'if_dropped']:
        return ('%s___%s' %(data['plugin_instance'], data['type']))

def virt(data):
    if data['type'] == 'percent' and data['type_instance'] == 'virt_cpu_total':
        return 'cpu_usage'

    if data['type'] == 'memory' and data['type_instance'] == 'unused':
        return 'memory_free'

    if (data['type'] in ['if_octets', 'if_packets', 'if_dropped']):
        return ('%s___%s' %(data['type_instance'], data['type']))

def ping(data):
    if data['type'] == 'ping':
        other_host = data['type_instance']
        if ping_cfg is not None:
            other_host = other_host.replace(ping_cfg["subnet"], ping_cfg["text"])
            if ping_cfg["replace_dot_by_slash"] is True:
                other_host = other_host.replace('.', '-')

        return ('%s___%s' %(other_host, data['type']))
