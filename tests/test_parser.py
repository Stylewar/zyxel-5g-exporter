import pathlib
import unittest
from unittest import mock

import cellwan_exporter


class ParseCellwanStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        example_path = pathlib.Path(__file__).resolve().parents[1] / "example_output.txt"
        cls.sample_output = example_path.read_text(encoding="utf-8")

    def setUp(self):
        cellwan_exporter.mark_scrape_failed()

    def test_parses_top_level_status_fields(self):
        data = cellwan_exporter.parse_cellwan_status(self.sample_output)

        self.assertEqual(data["Status"], "Up")
        self.assertEqual(data["Current Access Technology"], "NR5G-NSA")
        self.assertEqual(data["Current Band"], "LTE_BC3")
        self.assertEqual(data["Current CA combination"], "BC3,BC7,BC1,BC20,N28")

    def test_parses_nr5g_section(self):
        data = cellwan_exporter.parse_cellwan_status(self.sample_output)
        nr5g = data["nr5g"]

        self.assertEqual(nr5g["MCC"], "262")
        self.assertEqual(nr5g["NNC"], "03")
        self.assertEqual(nr5g["Band"], "NR5G_N28")
        self.assertEqual(nr5g["DL Bandwidth (MHz)"], "10")

    def test_parses_scc_sections(self):
        data = cellwan_exporter.parse_cellwan_status(self.sample_output)
        scc = data["scc"]

        self.assertEqual(sorted(scc.keys()), ["1", "2", "3"])
        self.assertEqual(scc["1"]["Band"], "LTE_BC7")
        self.assertEqual(scc["2"]["RFCN"], "300")
        self.assertEqual(scc["3"]["DownlinkBandwidth (MHZ)"], "10")

    def test_parses_neighbor_list(self):
        data = cellwan_exporter.parse_cellwan_status(self.sample_output)
        neighbors = data["neighbors"]

        self.assertEqual(len(neighbors), 7)
        self.assertEqual(neighbors[0]["type"], "Intra-Frequency")
        self.assertEqual(neighbors[0]["rfcn"], "1600")
        self.assertEqual(neighbors[-1]["physical_cell_id"], "120")

    def test_normalize_band_name(self):
        self.assertEqual(cellwan_exporter.normalize_band_name("LTE_BC20"), "B20")
        self.assertEqual(cellwan_exporter.normalize_band_name("BC7"), "B7")
        self.assertEqual(cellwan_exporter.normalize_band_name("NR5G_N28"), "n28")
        self.assertEqual(cellwan_exporter.normalize_band_name("n41"), "n41")
        self.assertIsNone(cellwan_exporter.normalize_band_name("N/A"))

    def test_update_metrics_replaces_old_labeled_series(self):
        first = cellwan_exporter.parse_cellwan_status(self.sample_output)
        second = cellwan_exporter.parse_cellwan_status(self.sample_output)
        second["Current Band"] = "LTE_BC1"
        second["Cell ID"] = "999"
        second["eNodeB ID"] = "777"
        second["Current CA combination"] = "BC1"
        second["nr5g"] = {}
        second["scc"] = {}
        second["neighbors"] = []

        cellwan_exporter.update_metrics(first)
        cellwan_exporter.update_metrics(second)

        primary_samples = list(cellwan_exporter.cellwan_primary_rssi.collect())[0].samples
        primary_labels = [sample.labels for sample in primary_samples]

        self.assertIn(
            {"band": "LTE_BC1", "cell_id": "999", "enodeb_id": "777"},
            primary_labels,
        )
        self.assertNotIn(
            {"band": "LTE_BC3", "cell_id": "26177578", "enodeb_id": "102256"},
            primary_labels,
        )
        self.assertEqual(list(cellwan_exporter.cellwan_neighbor_rssi.collect())[0].samples, [])
        self.assertEqual(list(cellwan_exporter.cellwan_scc_rssi.collect())[0].samples, [])
        ca_band_labels = [sample.labels for sample in list(cellwan_exporter.cellwan_ca_band_active.collect())[0].samples]
        self.assertEqual(ca_band_labels, [{"band": "B1"}])

    def test_mark_scrape_failed_clears_router_metrics(self):
        data = cellwan_exporter.parse_cellwan_status(self.sample_output)
        cellwan_exporter.update_metrics(data)

        cellwan_exporter.mark_scrape_failed()

        self.assertEqual(cellwan_exporter.cellwan_status_up._value.get(), 0.0)
        self.assertEqual(cellwan_exporter.cellwan_scrape_success._value.get(), 0.0)
        self.assertEqual(list(cellwan_exporter.cellwan_primary_rssi.collect())[0].samples, [])
        self.assertEqual(list(cellwan_exporter.cellwan_ca_band_active.collect())[0].samples, [])
        info_samples = list(cellwan_exporter.cellwan_info.collect())[0].samples
        self.assertEqual(info_samples[0].labels["network"], "N/A")

    def test_update_metrics_emits_active_ca_bands(self):
        data = cellwan_exporter.parse_cellwan_status(self.sample_output)

        cellwan_exporter.update_metrics(data)

        labels = [sample.labels["band"] for sample in list(cellwan_exporter.cellwan_ca_band_active.collect())[0].samples]
        self.assertEqual(labels, ["B1", "B3", "B7", "B20", "n28"])

    @mock.patch("cellwan_exporter.subprocess.run")
    def test_fetch_uses_argument_list_without_shell(self, run_mock):
        run_mock.return_value = mock.Mock(returncode=0, stdout="Status: Up\r\n", stderr="")

        output = cellwan_exporter.fetch_cellwan_status("router.local", "admin", "pa'ss")

        self.assertEqual(output, "Status: Up\n")
        args, kwargs = run_mock.call_args
        self.assertIsInstance(args[0], list)
        self.assertEqual(args[0][0:4], ["sshpass", "-p", "pa'ss", "ssh"])
        self.assertEqual(kwargs["input"], "cfg cellwan_status get\nexit\n")
        self.assertNotIn("shell", kwargs)


if __name__ == "__main__":
    unittest.main()
