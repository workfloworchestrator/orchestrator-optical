# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Client for executing TL1 commands on FlexILS devices through TNMS.

To add a new command, create a new module in the commands folder and
use the generator script in utils to create the Pydantic model for the
command help text that you can copy from a TL1 session on any FlexILS.

"""
