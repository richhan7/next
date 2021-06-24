"""
vefify_test.py

"""
import logging
import re

from pyats import aetest
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError
from genie.testbed import load
from genie.conf import Genie
from genie import parsergen
import re

from pprint import pprint

# create a logger for this module
logger = logging.getLogger(__name__)


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def load_testbed(self, testbed):
        logger.info(
            "Converting pyATS testbed to Genie Testbed to support pyATS Library features"
        )
        testbed = load(testbed)
        self.parent.parameters.update(testbed=testbed)

    @aetest.subsection
    def connect(self, testbed):
        """
        Connect to the devices
        """
        assert testbed, "Testbed is not provided!"

        # Connect to all testbed devices
        try:
            for device in testbed:
                device.connect()
        except (TimeoutError, StateMachineError, ConnectionError):
            logger.error("Unable to connect to all devices")


class verify_test(aetest.Testcase):
    """Verify that Memory level is within threshhold

    """

    @aetest.test
    def test_connection(self, testbed, steps):
        # Loop over every device in the testbed
        for device_name, device in testbed.devices.items():
            with steps.start(
                f"Test Connection Status of {device_name}", continue_=True
            ) as step:
                # Test "connected" status
                if device.connected:
                    logger.info(f"{device_name} connected status: {device.connected}")
                # Step fails if connection fails
                else:
                    logger.error(f"{device_name} connected status: {device.connected}")
                    step.failed()



    @aetest.test
    def test_last_reload(self, testbed, steps):
        # Loop over every device in the testbed
        for device_name, device in testbed.devices.items():
            
            with steps.start(
                f"Test last reload of {device_name}", continue_=True
            ) as step:
                if device.os in ("ios", "nxos"):
                    if device.connected:
                        # Parse show version
                        show_version_output = device.parse("show version")
                        print(show_version_output)
                        # If the upptime was more than 1 day, we log it as passing. If not, we mark it as failed
                        if show_version_output['platform']['kernel_uptime']['days'] > 1:
                            logger.info(f"{device_name}, {show_version_output['platform']['kernel_uptime']['days']} There was no reload within 1 day : {device.connected}")
                        else:
                            logger.error(f"{device_name}, {show_version_output['platform']['kernel_uptime']['days']} There was recent reload within 1 day: {device.connected}")
                            step.failed()
                if device.os in ("iosxe"):
                    if device.connected:
                        # Parse show version
                        show_version_output = device.parse("show version")
                        print(show_version_output)
                        # If the upptime was more than 1 day, we log it as passing. If not, we mark it as failed
                        if not '0 weeks' in show_version_output['version']['uptime']:
                            if not '0 days' in show_version_output['version']['uptime']:
                                logger.info(f"{device_name}, {show_version_output['version']['uptime']} There was no reload within 1 day : {device.connected}")
                            else:
                                logger.error(f"{device_name}, {show_version_output['version']['uptime']} There was recent reload within 1 day: {device.connected}")
                                step.failed()
                if device.os in ("asa"):
                    if device.connected:
                        # Execute show version for ASA
                        show_version_output = device.execute("show version")
                        print(show_version_output)
                        up_time = [line for line in show_version_output.splitlines() if 'up ' in line]
                        # If the upptime was more than 1 day, we log it as passing. If not, we mark it as failed
                        if not '0 weeks' in up_time:
                            if not '0 days' in up_time:
                                logger.info(f"{device_name}, {up_time} There was no reload within 1 day : {device.connected}")
                            else:
                                logger.error(f"{device_name}, {up_time} There was recent reload within 1 day: {device.connected}")
                                step.failed()
                if device.os in ("fxos"):
                    if device.connected:
                        # Execute show version for FXOS
                        show_version_output = device.execute("show version system")
                        print(show_version_output)
                        up_time = [line for line in show_version_output.splitlines() if 'up ' in line]
                        # If the upptime was more than 1 day, we log it as passing. If not, we mark it as failed
                        if not '0 weeks' in up_time:
                            if not '0 days' in up_time:
                                logger.info(f"{device_name}, {up_time} There was no reload within 1 day : {device.connected}")
                            else:
                                logger.error(f"{device_name}, {up_time} There was recent reload within 1 day: {device.connected}")
                                step.failed()


    @aetest.test
    def test_updown_validation(self, testbed, steps):
        # Loop over every device in the testbed
        for device_name, device in testbed.devices.items():
            with steps.start(
                f"Test Up/Down Status of {device_name}", continue_=True
            ) as device_step:
                if device.os in ('iosxe'):
                    if device.connected:
                        # Use the parse command below to get the output. 
                        intf_output = device.parse('show ip interface brief')
                        # For each interface in the output, use for loop to iterate over the JSON output.
                        for interface in intf_output['interface']:
                            with device_step.start(
                                f"Checking Interface Up/Down of {interface}", continue_=True
                            ) as interface_step:
                                # Set status with the obtained values from the JSON
                                status = intf_output['interface'][interface]['status']
                                # Set protocol with the obtained values from the JSON
                                protocol = intf_output['interface'][interface]['protocol']
                                # If both status and protocol are up, log as pass
                                if status == 'up' and protocol == 'up':
                                    logger.info("\nPASS: Interface {intf} status is: '{s}, {p}'".format(intf=interface, s=status, p=protocol))
                                # Else, mark it as failed
                                else:
                                    logger.info("\nFAIL: Interface {intf} status is: '{s}, {p}'".format(intf=interface, s=status, p=protocol))
                                    interface_step.failed()
                if device.os in ('nxos'):
                    if device.connected:
                        # Execute command below to get the output
                        intf_output = device.parse('show interface brief')
                        # For each interface in the output, use for loop to iterate over the JSON output
                        for interface in intf_output['interface']['ethernet']:
                            with device_step.start(
                                f"Checking Interface Up/Down of {interface}", continue_=True
                            ) as interface_step:
                                # Set status with the obtained values from the JSON
                                status = intf_output['interface']['ethernet'][interface]['status']
                                # If status is up, log as pass
                                if status == 'up':
                                    logger.info("\nPASS: Interface {intf} status is: '{s}'".format(intf=interface, s=status))
                                else:
                                    logger.info("\nFAIL: Interface {intf} status is: '{s}'".format(intf=interface, s=status))
                                    interface_step.failed()
                if device.os in ('asa'):
                    if device.connected:
                        # Execute command below to get the output with the newly created parsing.
                        output = device.execute("show interface ip brief")
                        # Set the headers for using parsergen
                        header=[ "Interface","IP-Address","OK\?","Method","Status","Protocol" ]
                        # Use parsergen to get the result
                        result = parsergen.oper_fill_tabular(device_output=output, device_os='asa', header_fields=header, index=[0])
                        pprint(result.entries)
                        # For each interface in the output, use for loop to iterate over output
                        for interface in result.entries:
                            with device_step.start(
                                f"Checking Interface Up/Down of {interface}", continue_=True
                            ) as interface_step:
                                # Set status with the obtained values from the JSON
                                status = result.entries[interface]['Status']
                                # Set pprotocol with the obtained values from the JSON                                
                                protocol = result.entries[interface]['Protocol']
                                # If both status and protocol are up, log as pass
                                if status == 'up' and protocol == 'up':
                                    logger.info("\nPASS: Interface {intf} status is: '{s}, {p}'".format(intf=interface, s=status, p=protocol))
                                # Else, mark it as fail. Interface step is failed
                                else:
                                    logger.info("\nFAIL: Interface {intf} status is: '{s}, {p}'".format(intf=interface, s=status, p=protocol))
                                    interface_step.failed()
                if device.os in ('fxos'):
                    if device.connected:
                        # Execute command below to get the output. Create new praser for fxos
                        output = device.execute("show interface ip brief")
                        # Set the headers for using parsergen
                        header=[ "Interface","IP-Address","OK\?","Method","Status","Protocol" ]
                        # Use parsergen to get the result
                        result = parsergen.oper_fill_tabular(device_output=output, device_os='asa', header_fields=header, index=[0])
                        pprint(result.entries)
                        # For each interface in the output, use for loop to iterate over output
                        for interface in result.entries:
                            with device_step.start(
                                f"Checking Interface Up/Down of {interface}", continue_=True
                            ) as interface_step:
                                # Set status with the obtained values from the JSON
                                status = result.entries[interface]['Status']
                                # Set pprotocol with the obtained values from the JSON                                                                
                                protocol = result.entries[interface]['Protocol']
                                # If both status and protocol are up, log as pass
                                if status == 'up' and protocol == 'up':
                                    logger.info("\nPASS: Interface {intf} status is: '{s}, {p}'".format(intf=interface, s=status, p=protocol))
                                # Else, mark it as fail. Interface step is failed
                                else:
                                    logger.info("\nFAIL: Interface {intf} status is: '{s}, {p}'".format(intf=interface, s=status, p=protocol))
                                    interface_step.failed()


    @aetest.test
    def test_cpu_util(self, testbed, steps):
        # Loop over every device in the testbed
        for device_name, device in testbed.devices.items():
            
            with steps.start(
                f"Test cpu util of {device_name}", continue_=True
            ) as step:
                if device.os in ("ios", "iosxr", "nxos"):
                    if device.connected:
                        # Parse the command to get the output
                        cpu_util = device.parse("sh proc cpu")
                        # Get the CPU level
                        if cpu_util['kernel_percent']:
                            cpu_util_kernel = cpu_util['kernel_percent']
                            cpu_util_kernel = float(cpu_util_kernel)
                            print(cpu_util_kernel)
                            # If level is less than declared value, we mark it good - pass
                            if cpu_util['kernel_percent'] < 40.0:
                                logger.info(f"{device_name}, {cpu_util_kernel} cpu_util is good: {device.connected}")
                            else:
                                logger.error(f"{device_name}, {cpu_util_kernel} cpu_util is bad: {device.connected}")
                                step.failed()
                if device.os in ('asa'):
                    if device.connected:
                        # Execute the command as parser does not exist
                        output = device.execute('show cpu usage')
                        # Perform Regex to get the data
                        cpu_percent = re.findall(r'\d+%', output)
                        output = [i.strip('%') for i in cpu_percent]
                        output = [float(i) for i in output]
                        # If level is less than declared value, we mark it good - pass
                        for i in output:
                            if i < 40.0:
                                logger.info(f"{device_name}, {i}, cpu_util is good: {device.connected}")
                            else:
                                logger.error(f"{device_name}, {i}, cpu_util is bad: {device.connected}")
                                step.failed()
                if device.os in ('fxos'):
                    if device.connected:
                        # Execute the command as parser does not exist
                        output = device.execute('show cpu')
                        # Perform Regex to get the data
                        cpu_percent = re.findall(r'\d+%', output)
                        output = [i.strip('%') for i in cpu_percent]
                        final_cpu_util = [float(i) for i in output]
                        # If level is less than declared value, we mark it good - pass
                        for i in final_cpu_util:
                            if i < 40.0:
                                logger.info(f"{device_name}, {i}, cpu_util is good: {device.connected}")
                            else:
                                logger.error(f"{device_name}, {i}, cpu_util is bad: {device.connected}")
                                step.failed()
                if device.os in ("iosxe"):
                    if device.connected:
                        # Parse the command to get the output
                        cpu_util = device.parse("sh proc cpu")
                        # Compare the level with the declared value
                        if cpu_util['five_sec_cpu_total'] or cpu_util['one_min_cpu'] or cpu_util['five_min_cpu'] < 40:
                            logger.info(f"{device_name}, {cpu_util['five_sec_cpu_total'], cpu_util['one_min_cpu'], cpu_util['five_min_cpu']} cpu_util is good: {device.connected}")
                        else:
                            logger.error(f"{device_name}, {cpu_util['five_sec_cpu_total'], cpu_util['one_min_cpu'], cpu_util['five_min_cpu']} cpu_util is bad: {device.connected}")
                            step.failed()


    @aetest.test
    def test_memory_util(self, testbed, steps):
        # Loop over every device in the testbed
        for device_name, device in testbed.devices.items():
            
            with steps.start(
                f"Test memory utilization of {device_name}", continue_=True
            ) as step:
                if device.os in ("ios", "iosxr", "nxos"):
                    if device.connected:
                        # Execute command below to ge the output
                        output = device.execute("show system resource")
                        # Find the line 
                        memory_usage = [line for line in output.splitlines() if 'Memory usage' in line]
                        # Find all with the memory usage w/ regex
                        memory_usage_list = re.findall(r'\d+', str(memory_usage))
                        memory_comparison = [float(i) for i in memory_usage_list]
                        # Divide to get the percentage of the used memory
                        memory_util_percentage = memory_comparison[1] / memory_comparison[0]
                        print(memory_util_percentage)
                        # Compare and if it's below .8, we mark it sufficient for passing
                        if memory_util_percentage < .80:
                            logger.info(f"{device_name}, {memory_util_percentage} memory_util is good: {device.connected}")
                        else:
                            logger.error(f"{device_name}, {memory_util_percentage} memory_util is bad: {device.connected}")
                            step.failed()
                if device.os in ('iosxe'):
                    if device.connected:
                        # Execute command below to get the output
                        memory_output = device.execute('show platform software status control-processor brief')
                        # Perform Regex to get the output for specific OS varaint
                        memory_percent = re.findall(r'\d+%', memory_output)
                        # Strip out percent for simple comparison and for consistensy
                        stripped_memory = [i.strip('%') for i in memory_percent]
                        memory_comparison = [float(i) for i in stripped_memory]
                        # Compare and if it's below 80, we mark it sufficient for passing
                        if memory_comparison[0] < 80:
                            logger.info(f"{device_name}, {memory_comparison[0]}, cpu_util is good: {device.connected}")
                        else:
                            logger.error(f"{device_name}, {memory_comparison[0]}, cpu_util is bad: {device.connected}")
                            step.failed()
                if device.os in ('asa'):
                    if device.connected:
                        memory_output = device.execute('show memory')
                        ## Obtain line containing 'Used Memory' from device
                        memory_usage = [line for line in memory_output.splitlines() if 'Used memory' in line]
                        # Perform Regex to get the output for specific OS varaint
                        memory_percent = re.findall(r'\d+%', str(memory_usage))
                        stripped_memory = [i.strip('%') for i in memory_percent]
                        memory_comparison = [float(i) for i in stripped_memory]
                        # Compare and if it's below 80, we mark it sufficient for passing
                        if memory_comparison[0] < 80:
                            logger.info(f"{device_name}, {memory_comparison[0]}, cpu_util is good: {device.connected}")
                        else:
                            logger.error(f"{device_name}, {memory_comparison[0]}, cpu_util is bad: {device.connected}")
                            step.failed()
                if device.os in ('fxos'):
                    if device.connected:
                        memory_output = device.execute('show memory')
                        ## Obtain Used Memory from device
                        memory_usage = [line for line in memory_output.splitlines() if 'Used memory' in line]
                        # Perform Regex to get the output for specific OS varaint
                        memory_percent = re.findall(r'\d+%', str(memory_usage))
                        stripped_memory = [i.strip('%') for i in memory_percent]
                        memory_comparison = [float(i) for i in stripped_memory]
                        # Compare and if it's below 80, we mark it sufficient for passing
                        if memory_comparison[0] < 80:
                            logger.info(f"{device_name}, {memory_comparison[0]}, cpu_util is good: {device.connected}")
                        else:
                            logger.error(f"{device_name}, {memory_comparison[0]}, cpu_util is bad: {device.connected}")
                            step.failed()


# class CommonCleanup(aetest.CommonCleanup):
#     @aetest.subsection
#     def disconnect_device(self,testbed):
#         try:
#             for device in testbed:
#                 device.disconnect()
#         except (TimeoutError, StateMachineError, ConnectionError):
#             logger.error("Unable to disconnect to all devices")


if __name__ == "__main__":
    # for stand-alone execution
    import argparse
    from pyats import topology

    parser = argparse.ArgumentParser(description="standalone parser")
    parser.add_argument(
        "--testbed",
        dest="testbed",
        help="testbed YAML file",
        type=topology.loader.load,
        default=None,
    )

    # do the parsing
    args = parser.parse_known_args()[0]

    aetest.main(testbed=args.testbed)

