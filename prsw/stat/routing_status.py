"""Provides the Routing Status endpoint."""

import ipaddress

from collections import namedtuple

from prsw.validators import Validators


class RoutingStatus:
    """
    This data call returns a summary of the current BGP routing state of a given IP prefix 
    or ASN, as observed by the RIS route collectors. Historical lookups are supported - a query 
    has to be aligned to the times (00:00, 08:00 and 16:00 UTC) when RIS data has been collected.

    Reference: `<https://stat.ripe.net/docs/data_api#routing-status>`_

    =================== ===============================================================
    Property            Description
    =================== ===============================================================
    ``prefix``          The prefix this query is based on
    ``resource``        The ASN this query is based on.
    ``status``          The RPKI validity state, according to RIPE NCC's RPKI validator
    ``validating_roas`` A list if validating ROAs
    =================== ===============================================================

    .. code-block:: python

        import prsw

        ripe = prsw.RIPEstat()
        result = ripe.rpki_validation_status(3333, '193.0.0.0/21')

        print(result.status)

        for roa in result.validating_roas:
            # ROA(
            #   origin=3333,
            #   prefix=IPv4Network('193.0.0.0/21'),
            #   validity='valid',
            #   source='RIPE NCC RPKI Root',
            #   max_length=21
            # )

            print(roa.origin, roa.prefix, roa.validity, roa.source)
    """

    PATH = "/routing-status"
    VERSION = "3.0"
    resource_type = ""

    def __init__(self, RIPEstat, resource):
        """
        Initialize and request RoutingStatus.

        RIPEstat, resource

        :param resource: The ASN used to perform the RPKI validity state lookup.
        sam dont forget to write that IP addresses with no prefix will default to /32
        :param prefix: The prefix to perform the RPKI validity state lookup. Note the
            prefix’s length is also taken from this field.

        """
        params = {
            "preferred_version": RoutingStatus.VERSION,
            "resource": str(self._resource(resource)),
        }

        self._api = RIPEstat._get(RoutingStatus.PATH, params)

    def _resource(self, value):
        """Validate and return a valid resource value."""
        resource = None

        # check if resource is a valid ASN
        if Validators._validate_asn(str(value)):
            resource = int(value)
            RoutingStatus.resource_type = "asn"
        # check if resource is an IP network
        elif Validators._validate_ip_network(value):
            resource = ipaddress.ip_network(value)
            RoutingStatus.resource_type = "prefix"
        else:
            raise ValueError("Resource must either be valid ASN int or valid IP prefix")

        return resource

    @property
    def announced_space(self):
        """
        NEED TO UPDATE THIS SAM
        This contains information that are related to special purpose Internet number
        resources, e.g. private address space.

        .. code-block:: python

            contacts = ripe.abuse_contact_finder('192.0.0.0')

            contacts.global_network_info
            # GlobalNetworkInfo(description="", name="RIPE NCC PI Allocation")

            contacts.global_network_info.name
            # "RIPE NCC PI Allocation"

        """

        if RoutingStatus.resource_type == "asn":

            Versions = namedtuple("Versions", ["v4", "v6"])
            V4totals = namedtuple("V4totals", ["ips", "prefixes"])
            V6totals = namedtuple("V6totals", ["amount_of_48s", "prefixes"])

            v4 = V4totals(**self._api.data["announced_space"]["v4"])

            v6_tuple = {"amount_of_48s": self._api.data["announced_space"]["v6"]["48s"],
                        "prefixes": self._api.data["announced_space"]["v6"]["prefixes"]}
            v6 = V6totals(**v6_tuple)

            return Versions(v4, v6)

    @property
    def first_seen(self):

        First_seen = namedtuple("First_seen", ["time", "origin", "prefix"])
        
        return First_seen(**self._api.data["first_seen"])

    @property
    def last_seen(self):

        Last_seen = namedtuple("Last_seen", ["time", "origin", "prefix"])
        
        return Last_seen(**self._api.data["last_seen"])
    
    @property
    def observed_neighbours(self):

        return self._api.data["observed_neighbours"]

    @property
    def query_time(self):

        return self._api.data["query_time"]