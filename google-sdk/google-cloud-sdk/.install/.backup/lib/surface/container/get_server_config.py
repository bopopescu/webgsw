# Copyright 2015 Google Inc. All Rights Reserved.
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

"""Get Server Config."""
from googlecloudsdk.calliope import base
from googlecloudsdk.core import log
from googlecloudsdk.core import properties


class GetServerConfig(base.Command):
  """Get Container Engine server config."""

  def Run(self, args):
    adapter = self.context['api_adapter']

    project_id = properties.VALUES.core.project.Get(required=True)
    zone = properties.VALUES.compute.zone.Get(required=True)

    log.status.Print('Fetching server config for {zone}'.format(zone=zone))
    return adapter.GetServerConfig(project_id, zone)

  def Display(self, args, result):
    """This method is called to print the result of the Run() method.

    Args:
      args: The arguments that command was run with.
      result: The value returned from the Run() method.
    """
    self.format(result)
