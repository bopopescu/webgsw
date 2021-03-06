# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Delete node pool command."""
import argparse
from googlecloudsdk.calliope import actions
from googlecloudsdk.calliope import base
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_io


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Delete(base.Command):
  """Delete an existing node pool in a running cluster."""

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: An argparse.ArgumentParser-like object. It is mocked out in order
          to capture some information, but behaves like an ArgumentParser.
    """
    parser.add_argument(
        'name',
        metavar='NAME',
        help='The name of the node pool to delete.')
    parser.add_argument(
        '--timeout',
        type=int,
        default=1800,
        help=argparse.SUPPRESS)
    parser.add_argument(
        '--wait',
        action='store_true',
        default=True,
        help='Poll the operation for completion after issuing a delete '
        'request.')
    parser.add_argument(
        '--cluster',
        help='The cluster from which to delete the node pool.',
        action=actions.StoreProperty(properties.VALUES.container.cluster))

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    adapter = self.context['api_adapter']

    pool_ref = adapter.ParseNodePool(args.name)

    console_io.PromptContinue(
        message=('The following node pool will be deleted.\n'
                 '[{name}] in cluster [{clusterId}] in zone [{zone}]')
        .format(name=pool_ref.nodePoolId,
                clusterId=pool_ref.clusterId,
                zone=adapter.Zone(pool_ref)),
        throw_if_unattended=True,
        cancel_on_no=True)

    # Make sure it exists (will raise appropriate error if not)
    adapter.GetNodePool(pool_ref)

    op_ref = adapter.DeleteNodePool(pool_ref)

    if args.wait:
      adapter.WaitForOperation(
          op_ref,
          'Deleting node pool {0}'.format(pool_ref.clusterId),
          timeout_s=args.timeout)
      log.DeletedResource(pool_ref)

    return op_ref
