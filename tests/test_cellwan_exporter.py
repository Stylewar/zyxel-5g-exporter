import hashlib

from cellwan_exporter import (
    masked_imei,
    safe_float,
    safe_int,
    update_metrics,
    cellwan_neighbor_rsrp,
    cellwan_neighbor_rsrq,
    cellwan_neighbor_rssi,
    cellwan_scc_bandwidth_dl,
    cellwan_scc_rfcn,
    cellwan_scc_rsrp,
    cellwan_scc_rsrq,
    cellwan_scc_rssi,
    cellwan_scc_sinr,
)


def reset_multi_label_metrics():
    cellwan_scc_rssi.clear()
    cellwan_scc_rsrp.clear()
    cellwan_scc_rsrq.clear()
    cellwan_scc_sinr.clear()
    cellwan_scc_bandwidth_dl.clear()
    cellwan_scc_rfcn.clear()
    cellwan_neighbor_rssi.clear()
    cellwan_neighbor_rsrp.clear()
    cellwan_neighbor_rsrq.clear()


def test_safe_int_handles_invalid_values():
    assert safe_int('N/A') is None
    assert safe_int(' 42 ') == 42
    assert safe_int('invalid', default=-1) == -1


def test_safe_float_handles_invalid_values():
    assert safe_float('N/A') is None
    assert safe_float(' 3.14 ') == 3.14
    assert safe_float('bad', default=1.5) == 1.5


def test_masked_imei_hashes_value():
    imei = '351955791157381'
    masked = masked_imei(imei)
    expected_suffix = hashlib.sha256(imei.encode('utf-8')).hexdigest()[:12]
    assert masked == f'sha256_{expected_suffix}'
    assert masked_imei('N/A') == 'unknown'


def test_update_metrics_clears_scc_and_neighbor_metrics():
    reset_multi_label_metrics()
    populated_payload = {
        'IMEI': '351955791157381',
        'Module Software Version': 'RG520FEBDER03A01M8G_OCPU_ZYXEL',
        'Network In Use': 'Current_o2 - de_NR5G-NSA_26203',
        'Current Access Technology': 'NR5G-NSA',
        'Current CA combination': 'BC3,BC7,BC1,BC20,N28',
        'Status': 'Up',
        'Current Band': 'LTE_BC3',
        'Cell ID': '26177578',
        'eNodeB ID': '102256',
        'RSSI': '-41',
        'RSRP': '-76',
        'RSRQ': '-13',
        'SINR': '22',
        'CQI': '12',
        'MCS': '18',
        'RI': '1',
        'PMI': '2',
        'UL Bandwidth (MHz)': '20',
        'DL Bandwidth (MHz)': '20',
        'Physical Cell ID': '148',
        'RFCN': '1600',
        'nr5g': {
            'Band': 'NR5G_N28',
            'MCC': '262',
            'MNC': '03',
            'RSRP': '-67',
            'RSRQ': '-11',
            'SINR': '30',
            'DL Bandwidth (MHz)': '10',
            'Physical Cell ID': '415',
            'RFCN': '152690',
        },
        'scc': {
            '1': {
                'Band': 'LTE_BC7',
                'Physical Cell ID': '128',
                'RSSI': '-56',
                'RSRP': '-88',
                'RSRQ': '-13',
                'SINR': '19',
                'DownlinkBandwidth (MHZ)': '20',
                'RFCN': '3350',
            }
        },
        'neighbors': [
            {
                'index': '1',
                'type': 'Intra-Frequency',
                'mode': 'LTE',
                'physical_cell_id': '148',
                'rfcn': '1600',
                'rssi': '-43',
                'rsrp': '-76',
                'rsrq': '-12',
            }
        ],
    }
    update_metrics(populated_payload)
    assert ('1', 'LTE_BC7', '128') in cellwan_scc_rssi._metrics
    assert ('1', 'Intra-Frequency', 'LTE', '148', '1600') in cellwan_neighbor_rssi._metrics

    update_metrics({
        'IMEI': '351955791157381',
        'Module Software Version': 'RG520FEBDER03A01M8G_OCPU_ZYXEL',
        'Network In Use': 'Current_o2 - de_NR5G-NSA_26203',
        'Current Access Technology': 'NR5G-NSA',
        'Current CA combination': 'BC3,BC7,BC1,BC20,N28',
        'Status': 'Up',
        'Current Band': 'LTE_BC3',
        'Cell ID': '26177578',
        'eNodeB ID': '102256',
        'scc': {},
        'neighbors': [],
    })

    assert cellwan_scc_rssi._metrics == {}
    assert cellwan_scc_rsrp._metrics == {}
    assert cellwan_scc_rsrq._metrics == {}
    assert cellwan_scc_sinr._metrics == {}
    assert cellwan_scc_bandwidth_dl._metrics == {}
    assert cellwan_scc_rfcn._metrics == {}
    assert cellwan_neighbor_rssi._metrics == {}
    assert cellwan_neighbor_rsrp._metrics == {}
    assert cellwan_neighbor_rsrq._metrics == {}
