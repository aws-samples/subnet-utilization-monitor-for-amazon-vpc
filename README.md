# IP Usage Monitor

This sample deploys a Lambda function that monitors IPv4 utilization for Amazon VPC Subnets and published the metrics to CloudWatch as custom metrics. The following metrics are published.

## `IPUsage/AvailableIPs`

Gives a count of the total number of IPv4 addresses available in the subnet.

## `IPUsage/TotalIPs`

Gives a count of the total possible IPv4 addresses in the subnet CIDR (based on the prefix, not usable IPs).

## `IPUsage/UsedIPs`

Gives the count of IPv4 addresses current used including reserved IP addresses and IP addresses used by ENIs.

## `IPUsage/Utilization`

Shows the percentage (as a float, not decimal representation of the percentage) of IPv4 space unusable in the subnet.


## Launch Instructions

To launch this sample, download the [CloudFormation YAML file](cloudformation/ip-allocation-monitor.yml) in the `cloudformation` directory and launch the template in each AWS region and account you wish to monitor subnet IPv4 utilization in.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file.

