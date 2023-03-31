#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import logging
from datetime import datetime
from ipaddress import ip_network

import boto3

ec2_client = boto3.client('ec2')
cloudwatch_client = boto3.client('cloudwatch')


def get_usage():
    subnet_data = dict()
    paginator = ec2_client.get_paginator('describe_subnets')
    iterator = paginator.paginate()
    for page in iterator:
        for subnet in page['Subnets']:
            logging.info(str(subnet))
            if not subnet['Ipv6Native']:
                try:
                    number_of_addresses = ip_network(subnet['CidrBlock']).num_addresses
                except:
                    logging.warning("Could not decipher Subnet CIDR.")
                    number_of_addresses = 0
                try:
                    available_addresses = int(subnet['AvailableIpAddressCount'])
                except:
                    logging.warning("Could not decipher available IPs.")
                    available_addresses = 0
                used_ips = number_of_addresses - available_addresses
                if number_of_addresses:
                    utilization = (used_ips / number_of_addresses) * 100
                else:
                    utilization = 1
                subnet_data[subnet['SubnetId']] = {
                    'VpcId': subnet['VpcId'],
                    'AvailableIPs': available_addresses,
                    'TotalIPs': number_of_addresses,
                    'UsedIPs': used_ips,
                    'Utilization': utilization
                }
    return subnet_data


def post_metric(metric_name: str, subnet_id: str, vpc_id: str, value: float, unit: str):
    cloudwatch_client.put_metric_data(
        Namespace='IPUsage',
        MetricData=[
            {
                'MetricName': metric_name,
                'Dimensions': [
                    {
                        'Name': 'SubnetId',
                        'Value': subnet_id
                    },
                    {
                        'Name': 'VpcId',
                        'Value': vpc_id
                    }
                ],
                'Timestamp': datetime.utcnow(),
                'Value': value,
                'Unit': unit
            }
        ]
    )


def post_usage(subnet_data):
    for subnet in subnet_data.keys():
        try:
            post_metric('AvailableIPs', str(subnet), str(subnet_data[subnet]['VpcId']),
                        float(subnet_data[subnet]['AvailableIPs']), 'Count')
        except:
            logging.critical("Could not post Available IPs metric for " + str(subnet))
        try:
            post_metric('TotalIPs', str(subnet), str(subnet_data[subnet]['VpcId']),
                        float(subnet_data[subnet]['TotalIPs']), 'Count')
        except:
            logging.critical("Could not post Total IPs metric for " + str(subnet))
        try:
            post_metric('UsedIPs', str(subnet), str(subnet_data[subnet]['VpcId']),
                        float(subnet_data[subnet]['UsedIPs']), 'Count')
        except:
            logging.critical("Could not post Used IPs metric for " + str(subnet))
        try:
            post_metric('Utilization', str(subnet), str(subnet_data[subnet]['VpcId']),
                        float(subnet_data[subnet]['Utilization']), 'Percent')
        except:
            logging.critical("Could not post Utilization metric for " + str(subnet))


def main(event, context):
    subnet_data = get_usage()
    post_usage(subnet_data)
