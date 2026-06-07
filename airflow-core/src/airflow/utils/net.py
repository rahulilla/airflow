#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

import socket
from functools import cache


# patched version of socket.getfqdn() - see https://github.com/python/cpython/issues/49254
@cache
def getfqdn(name=""):
    """
    Get fully qualified domain name from name.

    An empty argument is interpreted as meaning the local host.
    """
    name = name.strip()
    if not name or name == "0.0.0.0":
        name = socket.gethostname()
    try:
        addrs = socket.getaddrinfo(name, None, 0, socket.SOCK_DGRAM, 0, socket.AI_CANONNAME)
    except OSError:
        pass
    else:
        for addr in addrs:
            if addr[3]:
                name = addr[3]
                break
    return name


def get_host_ip_address():
    """Fetch host ip address."""
    return socket.gethostbyname(getfqdn())


def get_hostname():
    """Fetch the hostname using the callable from config or use `airflow.utils.net.getfqdn` as a fallback."""
    from airflow.configuration import conf

    return conf.getimport("core", "hostname_callable", fallback="airflow.utils.net.getfqdn")()


def is_valid_hostname(hostname: str) -> bool:
    """Return True if ``hostname`` is a syntactically valid DNS hostname.

    A valid hostname is at most 253 characters and consists of dot-separated
    labels, each 1-63 characters of letters, digits, or hyphens (not starting
    or ending with a hyphen).
    """
    if not hostname or len(hostname) > 253:
        return False
    hostname = hostname.rstrip(".")
    labels = hostname.split(".")
    for label in labels:
        if not 1 <= len(label) <= 63:
            return False
        if label.startswith("-") or label.endswith("-"):
            return False
        if not all(ch.isalnum() or ch == "-" for ch in label):
            return False
    return True
