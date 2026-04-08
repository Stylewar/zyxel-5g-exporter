import pathlib
import unittest

import cellwan_exporter


class ParseCellwanStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        example_path = pathlib.Path(__file__).resolve().parents[1] / "example_output.txt"
        cls.sample_output = example_path.read_text(encoding="utf-8")

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


if __name__ == "__main__":
    unittest.main()
