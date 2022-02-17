"""Test prsw.stat.routing_status"""

import ipaddress
import pytest
from datetime import datetime
from typing import Iterable
from unittest.mock import MagicMock, Mock, patch
from collections import namedtuple

from .. import UnitTest

from prsw.api import API_URL, Output
from prsw.stat.routing_status import RoutingStatus


class TestRoutingStatus(UnitTest):
    RESPONSE = {
        "messages": [
            [
                "info",
                "Results exclude routes with very low visibility (less than 10 RIS full-feed peers seeing)."
            ],
            [
                "warning",
                "Given query time (2021-05-15 08:00:00 UTC) has been changed because it is earlier than the time there is data available for!"
            ]
        ],
        "see_also": [],
        "version": "3.4",
        "data_call_status": "supported - connecting to ursa",
        "cached": False,
        "data": {
            "first_seen": {
                "prefix": "130.38.0.0/16",
                "origin": "196",
                "time": "2000-08-18T08:00:00"
            },
            "last_seen": {
                "prefix": "2001:1840:c000::/44",
                "origin": "196",
                "time": "2021-05-15T08:00:00"
            },
            "visibility": {
                "v4": {
                    "ris_peers_seeing": 328,
                    "total_ris_peers": 328
                },
                "v6": {
                    "ris_peers_seeing": 339,
                    "total_ris_peers": 339
                }
            },
            "announced_space": {
                "v4": {
                    "prefixes": 9,
                    "ips": 65536
                },
                "v6": {
                    "prefixes": 3,
                    "48s": 48
                }
            },
            "observed_neighbours": 1,
            "resource": "196",
            "query_time": "2021-05-15T08:00:00"
        },
        "query_id": "20210515165648-aa9b1828-ee97-4eea-a6fa-f932715dab23",
        "process_time": 1863,
        "server_id": "app142",
        "build_version": "live.2021.5.11.163",
        "status": "ok",
        "status_code": 200,
        "time": "2021-05-15T16:56:50.312331"
    }

    def setup(self):
        url = f"{API_URL}{RoutingStatus.PATH}data.json?resource=196"

        self.api_response = Output(url, **TestRoutingStatus.RESPONSE)
        self.params = {
            "preferred_version": RoutingStatus.VERSION,
            "resource": "196",
        }

        return super().setup()
    
    @pytest.fixture(scope="session")
    def mock_get(self):
        self.setup()

        with patch.object(self.ripestat, "_get") as mocked_get:
            mocked_get.return_value = self.api_response

            yield self

            mocked_get.assert_called_with(RoutingStatus.PATH, self.params)
            

    def test__init__valid_resource_asn(self, mock_get):
        response = RoutingStatus(mock_get.ripestat, self.params["resource"])
        assert isinstance(response, RoutingStatus)

    def test__init__invalid_asn_resources(self, mock_get):
        test_resources = [-1, "abcdef"]

        for resource in test_resources:
            with pytest.raises(ValueError):
                RoutingStatus(mock_get.ripestat, resource)

    
    def test_announced_space(self, mock_get):
        mock_get.params = self.params # reset params

        response = RoutingStatus(mock_get.ripestat, 196)

        assert isinstance(response.announced_space, tuple)
        assert type(response.announced_space).__name__ == "Versions"

        assert "ips" in response.announced_space.v4.__dir__()
        assert "prefixes" in response.announced_space.v4.__dir__()
        assert "amount_of_48s" in response.announced_space.v6.__dir__()
        assert "prefixes" in response.announced_space.v6.__dir__()
        
        expected_v4 = self.RESPONSE["data"]["announced_space"]["v4"]
        expected_v6 = self.RESPONSE["data"]["announced_space"]["v6"]

        assert response.announced_space.v4._asdict() == expected_v4

        assert response.announced_space.v6.amount_of_48s == expected_v6["48s"]
        assert response.announced_space.v6.prefixes == expected_v6["prefixes"]

    def test_first_seen(self, mock_get):
        mock_get.params = self.params # reset params

        response = RoutingStatus(mock_get.ripestat, 196)

        print(response.first_seen)

        assert isinstance(response.first_seen, tuple)

    def test_last_seen(self, mock_get):
        mock_get.params = self.params # reset params

        response = RoutingStatus(mock_get.ripestat, 196)

        print(response.last_seen)

        assert isinstance(response.last_seen, tuple)