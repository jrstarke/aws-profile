#!/usr/bin/env python
# There is a standard way to configure clients to assume role for a profile. See:
#     http://docs.aws.amazon.com/cli/latest/topic/config-vars.html#using-aws-iam-roles
# However, not all AWS SDKs support this AssumeRole configuration (yet).
#
# This script processes the configuration using boto (which supports this) and exports
#     environment variables which are standardised for use with less current SDKs
#
import argparse
import json
import os
import sys
import subprocess

import botocore.session

from awscli.utils import json_encoder
from awscli.customizations.assumerole import JSONFileCache
# JSONFileCache from awscli does not serialize datetime, add json_encoder support
class FixedJSONFileCache(JSONFileCache):
    def __setitem__(self, cache_key, value):
        full_key = self._convert_cache_key(cache_key)
        try:
            file_content = json.dumps(value, default=json_encoder)
        except (TypeError, ValueError):
            raise ValueError("Value cannot be cached, must be "
                             "JSON serializable: %s" % value)
        if not os.path.isdir(self._working_dir):
            os.makedirs(self._working_dir)
        with os.fdopen(os.open(full_key,
                               os.O_WRONLY | os.O_CREAT, 0o600), 'w') as f:
            f.truncate()
            f.write(file_content)

def configure_cache(session):
    """ Injects caching to the session's credential provider """
    cred_chain = session.get_component('credential_provider')
    provider = cred_chain.get_provider('assume-role')
    provider.cache = FixedJSONFileCache()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--profile",
                        help="set the AWS profile to use, this would override AWS environment variables",
                        required=False,
                        default=None)
    parser.add_argument("-r", "--region",
                        help="set the AWS region to use, this would override AWS environment variables",
                        required=False,
                        default=None)

    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    cache = os.getenv('AWS_CACHE','true')

    if cache.lower() != 'false':
        cache = 'true'
    else:
        cache = 'false'

    if not args.command:
        parser.print_help()
        sys.exit(1)
    return (args.profile, args.region, args.command, cache)


def main():
    profile, region, command, cache = parse_args()
    session = botocore.session.Session(profile=profile)
    if cache == 'true':
        configure_cache(session)
    config = session.get_scoped_config()
    creds = session.get_credentials()

    # Unset variables for sanity sake
    os.unsetenv('AWS_ACCESS_KEY_ID')
    os.unsetenv('AWS_SECRET_ACCESS_KEY')
    os.unsetenv('AWS_SESSION_TOKEN')

    region = region if region is not None else config.get('region', None)

    if profile:
        os.putenv('AWS_PROFILE', profile)

    if region:
        os.putenv('AWS_DEFAULT_REGION', region)
        os.putenv('AWS_REGION', region)

    os.putenv('AWS_ACCESS_KEY_ID', creds.access_key)
    os.putenv('AWS_SECRET_ACCESS_KEY', creds.secret_key)
    if creds.token:
        if os.getenv('AWS_TOKEN_TYPE') == 'security':
            os.putenv('AWS_SECURITY_TOKEN', creds.token)
        else:
            os.putenv('AWS_SESSION_TOKEN', creds.token)


    returncode = subprocess.call(
        command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr
    )

    exit(sys.exit(returncode))

if __name__ == '__main__':
    main()
