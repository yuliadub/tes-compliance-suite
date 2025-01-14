"""Module compliance_suite.cli.py

This module is the entry point for the compliance suite and contains a CLI functionality
"""

import os
from typing import List

import click

from compliance_suite.functions.log import logger
from compliance_suite.job_runner import JobRunner
from compliance_suite.report_server import ReportServer


@click.group()
def main() -> None:
    pass


@main.command(help='Run TES compliance tests against the servers')
@click.option('--server', '-s', help='server URL on which the compliance tests are run. Format - https://<url>/')
@click.option('--version', '-v', help='TES version. Example - "v1.0"')
@click.option('--tag', '-t', multiple=True, help='Tag', default=['All'])
@click.option('--output_path', '-o', help='path to output the JSON report')
@click.option('--serve', default=False, is_flag=True, help='spin up a server')
@click.option('--port', default=15800, help='port at which the compliance report is served')
@click.option('--uptime', '-u', default=3600, help='time that server will remain up in seconds')
def report(server: str,
           version: str,
           tag: List[str],
           output_path: str,
           serve: bool,
           port: int,
           uptime: int) -> None:
    """ Program entrypoint called via "report" in CLI.
    Run the compliance suite for the given tags.

    Args:
        server (str): The server URL on which the compliance suite will be run. Format - https://<url>/
        version (str): The compliance suite will be run against this TES version.
                       Default - Latest version. Example - "v1.0"
        tag (List[str]): The list of the tags for which the compliance suite will be run. Default - All
        output_path (str): The output path to store the JSON compliance report
        serve (bool): If true, runs a local server and displays the JSON report in webview
        port (int): Set the local server port. Default - 16800
        uptime (int): The local server duration in seconds. Default - 3600 seconds
    """

    if server is None:
        raise Exception("No server provided. Please provide a server URL.")

    if version is None:
        logger.info("No version provided. Latest version is used as default value.")
        version = "v1.0"                    # Hardcode the latest version here. TODO - Future versions

    tag = [val.lower() for val in tag]      # Convert the tags into lowercase to allow case-insensitive tags
    logger.info(f"Input tag is - {tag}")
    job_runner = JobRunner(server, version, tag)
    job_runner.run_jobs()

    json_report = job_runner.generate_report()

    # Store the report in given output path
    if output_path is not None:
        logger.info(f"Writing JSON Report on directory {output_path}")
        with open(os.path.join(output_path, "report.json"), "w+") as output:
            output.write(json_report)

    # Writing a report copy to web dir for local server
    with open(os.path.join(os.getcwd(), "compliance_suite", "web", "web_report.json"), "w+") as output:
        output.write(json_report)

    if serve is True:
        report_server = ReportServer(os.path.join(os.getcwd(), "compliance_suite", "web"))
        report_server.serve_thread(port, uptime)


if __name__ == "__main__":
    main()
