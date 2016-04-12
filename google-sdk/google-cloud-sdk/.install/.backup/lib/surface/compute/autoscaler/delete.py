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
"""Command for deleting autoscalers."""

from googlecloudsdk.api_lib.compute import autoscaler_utils as util
from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.core import log
from googlecloudsdk.third_party.apitools.base.py import exceptions


class DeleteAutoscaler(base_classes.BaseCommand):  # BaseAsyncMutator
  """Delete Autoscaler instances."""

  @staticmethod
  def Args(parser):
    parser.add_argument('names', help='Autoscalers names.', nargs='+')

  def Run(self, args):
    log.warn('Please use instead [gcloud compute instance-groups '
             'managed stop-autoscaling].')
    client = self.context['autoscaler-client']
    messages = self.context['autoscaler_messages_module']
    resources = self.context['autoscaler_resources']
    try:
      request = messages.AutoscalerAutoscalersDeleteRequest()
      for autoscaler in args.names:
        autoscaler_ref = resources.Parse(
            autoscaler, collection='autoscaler.autoscalers')
        request.autoscaler = autoscaler_ref.autoscaler
        request.project = autoscaler_ref.project
        request.zone = autoscaler_ref.zone
        result = client.autoscalers.Delete(request)
        operation_ref = resources.Create(
            'autoscaler.zoneOperations',
            operation=result.name,
            autoscaler=request.autoscaler,
        )
        util.WaitForOperation(client, operation_ref,
                              'Deleting Autoscaler instance')
        log.DeletedResource(autoscaler_ref)
    except exceptions.HttpError as error:
      raise calliope_exceptions.HttpException(util.GetErrorMessage(error))
    except ValueError as error:
      raise calliope_exceptions.HttpException(error)
