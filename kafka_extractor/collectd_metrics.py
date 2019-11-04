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
        # other host is IP address format: x.x.x.x. Re-format to NI-Compute-x-x
        other_host = other_host.split('.')
        other_host = "%s-%s-%s" %("NI-Compute", other_host[2], other_host[3])

        return ('%s___%s' %(other_host, data['type']))
