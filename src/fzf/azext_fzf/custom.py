# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from knack.util import CLIError
from iterfzf import iterfzf
from tabulate import tabulate

logger = get_logger(__name__)


def fzf_group(cmd):
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
        logger.warning('Please run "az login" to access your accounts.')
    
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
