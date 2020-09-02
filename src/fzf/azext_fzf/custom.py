# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
import json
import os
import platform
import shutil
import ssl
import stat
import sys
import tarfile

from azure.cli.core.api import get_config_dir
from knack.log import get_logger
from knack.util import CLIError
from pathlib import Path
from pprint import pprint
from tabulate import tabulate
from six.moves.urllib.request import urlopen  # pylint: disable=import-error
from six.moves.urllib.error import URLError  # pylint: disable=import-error


logger = get_logger(__name__)


def fzf_install(version='latest', install_dir=None):
    """
    Install fzf, a command line fuzzy finder.
    """

    system = platform.system()
    arch = platform.uname().processor
    if arch == 'x86_64': arch = 'amd64'

    if not install_dir:
        install_dir = get_config_dir()
    else:
        if system == 'Windows':  # be verbose, as the install_location likely not in Windows's search PATHs
            env_paths = os.environ['PATH'].split(';')
            found = next((x for x in env_paths if x.lower().rstrip('\\') == install_dir.lower()), None)
            if not found:
                # pylint: disable=logging-format-interpolation
                logger.warning('Please add "{0}" to your search PATH so the `fzf` can be found. 2 options: \n'
                            '    1. Run "set PATH=%PATH%;{0}" or "$env:path += \'{0}\'" for PowerShell. '
                            'This is good for the current command session.\n'
                            '    2. Update system PATH environment variable by following '
                            '"Control Panel->System->Advanced->Environment Variables", and re-open the command window. '
                            'You only need to do it once'.format(install_dir))
        else:
            logger.warning('Please ensure that %s is in your search PATH, so the `fzf` command can be found.',
                        install_dir)


    install_dir = os.path.expanduser(install_dir)
    install_location = os.path.join(install_dir, "fzf")
    repos_url = "https://api.github.com/repos/junegunn/fzf-bin/releases"

    logger.info(f'Downloading fzf-bin releases JSON from "{repos_url}"')
    context = ssl.create_default_context()
    releases_json = urlopen(repos_url, context=context).read().decode('UTF-8')
    releases = json.loads(releases_json)

    if version == 'latest':
        release = releases[0]
    else:
        release = next((r for r in releases if r["tag_name"] == version), None)

        if not release:
            raise CLIError(f'No release found for tag {version}.')
    
    file_url = next((asset["browser_download_url"] for asset in release["assets"] if (system.upper() in asset["name"].upper()) and (arch.upper() in asset["name"].upper())), None)
    if not file_url:
        raise CLIError(f'No download found for {system} {arch}')
    else:
        logger.info(f'Found download url "{file_url}"')

    if not os.path.exists(install_dir):
        os.makedirs(install_dir)

    logger.info('Downloading client to "%s" from "%s"', install_location, file_url)
    try:
        file_response = urlopen(file_url, context=context)
        compressed_file = io.BytesIO(file_response.read())
        tar = tarfile.open(fileobj=compressed_file)
        tar.extract("fzf", path=install_dir)

        os.chmod(install_location,
                 os.stat(install_location).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except IOError as ex:
        raise CLIError('Connection error while attempting to download client ({})'.format(ex))

    return


def _fzf(items, header_rows=0, exact=False, preview_command=''):
    search_path=":".join((get_config_dir(), os.environ.get('PATH')))
    fzf = shutil.which('fzf', path=search_path)
    if not fzf:
        raise CLIError('Couldn\'t find fzf. You can install it via `az fzf install`.')

    logger.info(f'Found fzf at {fzf}')


def fzf_group(cmd):
    _fzf(("test1", "test2"))
    return
    from azure.cli.command_modules.resource._client_factory import _resource_client_factory

    groups = list(_resource_client_factory(cmd.cli_ctx).resource_groups.list())
    groups_table = str(tabulate([[group.name, group.location] for group in groups], tablefmt='plain')).split('\n')
    result = iterfzf(groups_table, prompt='Resource group: ', preview='az group show -n {1}')

    if result:
        group = result.split(" ")[0]
        cmd.cli_ctx.config.set_value(cmd.cli_ctx.config.defaults_section_name, 'group', group)
        return next((g for g in groups if g.name == group), None)
    else:
        pass


def fzf_location(cmd):
    from azure.cli.core.commands.parameters import get_subscription_locations

    locations = get_subscription_locations(cmd.cli_ctx)
    locations_table = str(tabulate([[location.name, location.display_name, location.regional_display_name] for location in locations], tablefmt='plain')).split('\n')
    result = iterfzf(locations_table, prompt='Location: ', preview='az account list-locations --query "[?name == {1}]"')

    if result:
        location = result.split(" ")[0]
        cmd.cli_ctx.config.set_value(cmd.cli_ctx.config.defaults_section_name, 'location', location)
        return next((l for l in locations if l.name == location))
    else:
        pass


def fzf_subscription(cmd):
    from azure.cli.core._profile import Profile
    from azure.cli.core.api import load_subscriptions

    subscriptions = load_subscriptions(cmd.cli_ctx, all_clouds=False, refresh=False)

    if not subscriptions:
        raise CLIError('Please run "az login" to access your accounts.')
    
    for sub in subscriptions:
        sub['cloudName'] = sub.pop('environmentName', None)

    enabled_ones = [s for s in subscriptions if s.get('state') == 'Enabled']
    if len(enabled_ones) != len(subscriptions):
        logger.warning("A few accounts are skipped as they don't have 'Enabled' state.")
        subscriptions = enabled_ones

    if subscriptions:
        subscriptions_table = str(tabulate([[s["name"], s["id"]] for s in subscriptions], tablefmt='plain')).split('\n')
        result = iterfzf(subscriptions_table, prompt='Subscription: ', preview='az account show --subscription {-1}')

        if result:
            subscription = result.split(" ")[-1]
            Profile(cli_ctx=cmd.cli_ctx).set_active_subscription(subscription)
            return next((s for s in subscriptions if s["id"] == subscription))
        else:
            pass
    else:
        pass
