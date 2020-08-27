# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from knack.util import CLIError
from iterfzf import iterfzf

from azure.cli.core._profile import Profile

logger = get_logger(__name__)


def fzf_account_select(cmd, client):
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

    subscription = iterfzf([f'{sub["id"]}\t{sub["name"]}' for sub in subscriptions], prompt='Subscription: ', exact=True, preview='az account show --subscription {1}').split("\t")[0]

    profile = Profile(cli_ctx=cmd.cli_ctx)
    profile.set_active_subscription(subscription)

    return 
