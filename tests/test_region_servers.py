import unittest

from pypetkitapi.client import _group_region_servers
from pypetkitapi.const import PetkitDomain

SAMPLE_PAYLOAD = {
    "list": [
        {
            "accountType": "1",
            "gateway": "https://api.eu-pet.com/latest/",
            "id": "DE",
            "name": "Germany",
        },
        {
            "accountType": "1",
            "gateway": "https://api.eu-pet.com/latest/",
            "id": "FR",
            "name": "France",
        },
        {
            "accountType": "1",
            "gateway": "https://api.petkt.com/latest/",
            "id": "US",
            "name": "United States",
        },
    ]
}


class TestGroupRegionServers(unittest.TestCase):
    def test_groups_countries_by_gateway(self):
        groups = _group_region_servers(SAMPLE_PAYLOAD)
        eu = next(g for g in groups if g.gateway == "https://api.eu-pet.com/latest/")
        self.assertEqual(eu.countries, ["DE", "FR"])
        self.assertEqual(eu.representative_country, "DE")
        self.assertEqual(eu.label, "Europe")

    def test_appends_china_when_missing(self):
        groups = _group_region_servers(SAMPLE_PAYLOAD)
        china = next(
            (g for g in groups if g.gateway == PetkitDomain.CHINA_SRV.value), None
        )
        self.assertIsNotNone(china)
        self.assertEqual(china.countries, ["CN"])
        self.assertEqual(china.representative_country, "CN")
        self.assertEqual(china.label, "China")

    def test_does_not_duplicate_china_when_present(self):
        payload = {
            "list": [
                *SAMPLE_PAYLOAD["list"],
                {
                    "accountType": "1",
                    "gateway": PetkitDomain.CHINA_SRV.value,
                    "id": "CN",
                    "name": "China",
                },
            ]
        }
        groups = _group_region_servers(payload)
        china_groups = [g for g in groups if g.gateway == PetkitDomain.CHINA_SRV.value]
        self.assertEqual(len(china_groups), 1)

    def test_sorted_by_label(self):
        groups = _group_region_servers(SAMPLE_PAYLOAD)
        labels = [g.label for g in groups]
        self.assertEqual(labels, sorted(labels))

    def test_unknown_gateway_uses_url_as_label(self):
        payload = {
            "list": [
                {
                    "accountType": "1",
                    "gateway": "https://api.unknown.example/latest/",
                    "id": "ZZ",
                    "name": "Unknown",
                }
            ]
        }
        groups = _group_region_servers(payload)
        unknown = next(
            g for g in groups if g.gateway == "https://api.unknown.example/latest/"
        )
        self.assertEqual(unknown.label, "https://api.unknown.example/latest/")

    def test_empty_payload_still_returns_china(self):
        groups = _group_region_servers({"list": []})
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].gateway, PetkitDomain.CHINA_SRV.value)


if __name__ == "__main__":
    unittest.main()
