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

import random
import string


def generate_ctag():
    """
    Generates a 6-character correlation tag (CTAG) that is guaranteed
    to start with an alphabetic character if it contains any digits.
    """
    alphabet = string.ascii_uppercase
    alphanum = string.ascii_uppercase + string.digits
    first_char = random.choice(alphabet)
    remaining_chars = [random.choice(alphanum) for _ in range(5)]
    return first_char + "".join(remaining_chars)
