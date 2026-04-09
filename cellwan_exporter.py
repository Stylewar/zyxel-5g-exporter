#!/usr/bin/env python3
"""
Zyxel 5G Router Prometheus Exporter
Collects cellular WAN status via SSH and exposes metrics for Prometheus
"""

import argparse
import logging
import os
import re
import subprocess
import sys
import time
from threading import Lock
from prometheus_client import start_http_server, Gauge, Info
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Configure logging
log_level = logging.DEBUG if os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes') else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Define Prometheus metrics
cellwan_info = Info('cellwan', 'Cellular WAN information')
cellwan_status_up = Gauge('cellwan_status_up', 'Cellular WAN connection status')
cellwan_scrape_success = Gauge('cellwan_scrape_success', 'Whether the latest router scrape succeeded')

# Primary cell metrics
cellwan_primary_rssi = Gauge('cellwan_primary_rssi_dbm', 'Primary cell RSSI in dBm', ['band', 'cell_id', 'enodeb_id'])
cellwan_primary_rsrp = Gauge('cellwan_primary_rsrp_dbm', 'Primary cell RSRP in dBm', ['band', 'cell_id', 'enodeb_id'])
cellwan_primary_rsrq = Gauge('cellwan_primary_rsrq_db', 'Primary cell RSRQ in dB', ['band', 'cell_id', 'enodeb_id'])
cellwan_primary_sinr = Gauge('cellwan_primary_sinr_db', 'Primary cell SINR in dB', ['band', 'cell_id', 'enodeb_id'])
cellwan_primary_cqi = Gauge('cellwan_primary_cqi', 'Primary cell CQI', ['band', 'cell_id', 'enodeb_id'])
cellwan_primary_mcs = Gauge('cellwan_primary_mcs', 'Primary cell MCS', ['band', 'cell_id', 'enodeb_id'])
cellwan_primary_ri = Gauge('cellwan_primary_ri', 'Primary cell RI', ['band', 'cell_id', 'enodeb_id'])
cellwan_primary_pmi = Gauge('cellwan_primary_pmi', 'Primary cell PMI', ['band', 'cell_id', 'enodeb_id'])
cellwan_primary_bandwidth_ul = Gauge('cellwan_primary_bandwidth_ul_mhz', 'Primary cell uplink bandwidth in MHz', ['band', 'cell_id', 'enodeb_id'])
cellwan_primary_bandwidth_dl = Gauge('cellwan_primary_bandwidth_dl_mhz', 'Primary cell downlink bandwidth in MHz', ['band', 'cell_id', 'enodeb_id'])
cellwan_primary_physical_cell_id = Gauge('cellwan_primary_physical_cell_id', 'Primary cell physical cell ID', ['band', 'cell_id', 'enodeb_id'])
cellwan_primary_rfcn = Gauge('cellwan_primary_rfcn', 'Primary cell RFCN', ['band', 'cell_id', 'enodeb_id'])

# NR5G metrics
cellwan_nr5g_rsrp = Gauge('cellwan_nr5g_rsrp_dbm', 'NR5G RSRP in dBm', ['band', 'mcc', 'mnc'])
cellwan_nr5g_rsrq = Gauge('cellwan_nr5g_rsrq_db', 'NR5G RSRQ in dB', ['band', 'mcc', 'mnc'])
cellwan_nr5g_sinr = Gauge('cellwan_nr5g_sinr_db', 'NR5G SINR in dB', ['band', 'mcc', 'mnc'])
cellwan_nr5g_bandwidth_dl = Gauge('cellwan_nr5g_bandwidth_dl_mhz', 'NR5G downlink bandwidth in MHz', ['band', 'mcc', 'mnc'])
cellwan_nr5g_physical_cell_id = Gauge('cellwan_nr5g_physical_cell_id', 'NR5G physical cell ID', ['band', 'mcc', 'mnc'])
cellwan_nr5g_rfcn = Gauge('cellwan_nr5g_rfcn', 'NR5G RFCN', ['band', 'mcc', 'mnc'])

# SCC metrics
cellwan_scc_rssi = Gauge('cellwan_scc_rssi_dbm', 'Secondary carrier RSSI in dBm', ['scc_index', 'band', 'physical_cell_id'])
cellwan_scc_rsrp = Gauge('cellwan_scc_rsrp_dbm', 'Secondary carrier RSRP in dBm', ['scc_index', 'band', 'physical_cell_id'])
cellwan_scc_rsrq = Gauge('cellwan_scc_rsrq_db', 'Secondary carrier RSRQ in dB', ['scc_index', 'band', 'physical_cell_id'])
cellwan_scc_sinr = Gauge('cellwan_scc_sinr_db', 'Secondary carrier SINR in dB', ['scc_index', 'band', 'physical_cell_id'])
cellwan_scc_bandwidth_dl = Gauge('cellwan_scc_bandwidth_dl_mhz', 'Secondary carrier downlink bandwidth in MHz', ['scc_index', 'band', 'physical_cell_id'])
cellwan_scc_rfcn = Gauge('cellwan_scc_rfcn', 'Secondary carrier RFCN', ['scc_index', 'band', 'physical_cell_id'])

# Neighbor cell metrics
cellwan_neighbor_rssi = Gauge('cellwan_neighbor_rssi_dbm', 'Neighbor cell RSSI in dBm', ['neighbor_index', 'neighbor_type', 'mode', 'physical_cell_id', 'rfcn'])
cellwan_neighbor_rsrp = Gauge('cellwan_neighbor_rsrp_dbm', 'Neighbor cell RSRP in dBm', ['neighbor_index', 'neighbor_type', 'mode', 'physical_cell_id', 'rfcn'])
cellwan_neighbor_rsrq = Gauge('cellwan_neighbor_rsrq_db', 'Neighbor cell RSRQ in dB', ['neighbor_index', 'neighbor_type', 'mode', 'physical_cell_id', 'rfcn'])

# Helper metrics for current connection composition
cellwan_ca_band_active = Gauge('cellwan_ca_band_active', 'Whether a carrier aggregation band is currently active', ['band'])

# Lock for thread safety
metrics_lock = Lock()

UNKNOWN_INFO = {
    'network': 'N/A',
    'access_technology': 'N/A',
    'ca_combination': 'N/A'
}

LABELED_METRICS = (
    cellwan_primary_rssi,
    cellwan_primary_rsrp,
    cellwan_primary_rsrq,
    cellwan_primary_sinr,
    cellwan_primary_cqi,
    cellwan_primary_mcs,
    cellwan_primary_ri,
    cellwan_primary_pmi,
    cellwan_primary_bandwidth_ul,
    cellwan_primary_bandwidth_dl,
    cellwan_primary_physical_cell_id,
    cellwan_primary_rfcn,
    cellwan_nr5g_rsrp,
    cellwan_nr5g_rsrq,
    cellwan_nr5g_sinr,
    cellwan_nr5g_bandwidth_dl,
    cellwan_nr5g_physical_cell_id,
    cellwan_nr5g_rfcn,
    cellwan_scc_rssi,
    cellwan_scc_rsrp,
    cellwan_scc_rsrq,
    cellwan_scc_sinr,
    cellwan_scc_bandwidth_dl,
    cellwan_scc_rfcn,
    cellwan_neighbor_rssi,
    cellwan_neighbor_rsrp,
    cellwan_neighbor_rsrq,
    cellwan_ca_band_active,
)


def parse_value(line, pattern, default='N/A'):
    """Extract value from line using regex pattern"""
    match = re.search(pattern, line)
    return match.group(1).strip() if match else default


def parse_cellwan_status(output):
    """Parse cellwan_status output and update Prometheus metrics"""
    lines = output.split('\n')
    data = {}
    current_section = None
    scc_data = {}
    neighbor_data = []
    
    for line in lines:
        line = line.strip()
        
        # Detect sections
        if 'NR5G-NSA Information:' in line:
            current_section = 'nr5g'
            data['nr5g'] = {}
            continue
        elif 'SCC 1 information:' in line:
            current_section = 'scc1'
            scc_data['1'] = {}
            continue
        elif 'SCC 2 information:' in line:
            current_section = 'scc2'
            scc_data['2'] = {}
            continue
        elif 'SCC 3 information:' in line:
            current_section = 'scc3'
            scc_data['3'] = {}
            continue
        elif 'Neighbour list information:' in line:
            current_section = 'neighbors'
            continue
        elif current_section == 'neighbors' and line and not line.startswith('#'):
            # Parse neighbor line
            parts = line.split()
            if len(parts) >= 7:
                neighbor_data.append({
                    'index': parts[0],
                    'type': parts[1],
                    'mode': parts[2],
                    'physical_cell_id': parts[3],
                    'rfcn': parts[4],
                    'rssi': parts[5],
                    'rsrp': parts[6],
                    'rsrq': parts[7] if len(parts) > 7 else 'N/A'
                })
        
        # Parse key-value pairs
        if ':' in line:
            key_part = line.split(':', 1)[0].strip()
            value_part = line.split(':', 1)[1].strip() if len(line.split(':', 1)) > 1 else ''
            
            if current_section == 'nr5g':
                data['nr5g'][key_part] = value_part
            elif current_section in ['scc1', 'scc2', 'scc3']:
                scc_data[current_section[-1]][key_part] = value_part
            elif current_section is None:
                data[key_part] = value_part
    
    data['scc'] = scc_data
    data['neighbors'] = neighbor_data
    
    return data


def safe_int(value, default=0):
    """Safely convert value to int"""
    if value == 'N/A' or value == '':
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Safely convert value to float"""
    if value == 'N/A' or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def clear_router_metrics():
    """Remove all labeled series so stale cells do not linger across scrapes."""
    for metric in LABELED_METRICS:
        metric.clear()


def normalize_band_name(value):
    """Normalize Zyxel band strings to concise Grafana-friendly values."""
    if not value or value in ('N/A', 'unknown'):
        return None

    band = value.strip()

    lte_match = re.search(r'(?:LTE_)?BC(\d+)', band, re.IGNORECASE)
    if lte_match:
        return f"B{int(lte_match.group(1))}"

    nr_match = re.search(r'(?:NR5G_)?N(\d+)', band, re.IGNORECASE)
    if nr_match:
        return f"n{int(nr_match.group(1))}"

    return band


def iter_active_ca_bands(data):
    """Yield normalized active LTE/NR carrier aggregation bands for the current scrape."""
    bands = set()

    for raw_band in (data.get('Current Band'), data.get('Current CA combination')):
        if not raw_band:
            continue
        for part in raw_band.split(','):
            normalized = normalize_band_name(part)
            if normalized:
                bands.add(normalized)

    nr5g = data.get('nr5g', {})
    normalized_nr_band = normalize_band_name(nr5g.get('Band'))
    if normalized_nr_band:
        bands.add(normalized_nr_band)

    for scc_info in data.get('scc', {}).values():
        normalized_scc_band = normalize_band_name(scc_info.get('Band'))
        if normalized_scc_band:
            bands.add(normalized_scc_band)

    def sort_key(band):
        prefix = 0 if band.startswith('B') else 1
        return (prefix, int(re.search(r'(\d+)$', band).group(1)) if re.search(r'(\d+)$', band) else band)

    return sorted(bands, key=sort_key)


def mark_scrape_failed():
    """Reset scrape-dependent metrics after an SSH or parsing failure."""
    with metrics_lock:
        clear_router_metrics()
        cellwan_info.info(UNKNOWN_INFO)
        cellwan_status_up.set(0)
        cellwan_scrape_success.set(0)


def update_metrics(data):
    """Update Prometheus metrics with parsed data"""
    with metrics_lock:
        clear_router_metrics()

        # Info metric (IMEI and Module removed for data protection)
        cellwan_info.info({
            'network': data.get('Network In Use', 'N/A'),
            'access_technology': data.get('Current Access Technology', 'N/A'),
            'ca_combination': data.get('Current CA combination', 'N/A')
        })

        cellwan_scrape_success.set(1)
        status = data.get('Status', 'Down')
        cellwan_status_up.set(1 if status == 'Up' else 0)

        for active_band in iter_active_ca_bands(data):
            cellwan_ca_band_active.labels(band=active_band).set(1)

        band = data.get('Current Band', 'unknown')
        cell_id = data.get('Cell ID', 'unknown')
        enodeb_id = data.get('eNodeB ID', 'unknown')

        rssi = safe_float(data.get('RSSI'))
        if rssi is not None:
            cellwan_primary_rssi.labels(band=band, cell_id=cell_id, enodeb_id=enodeb_id).set(rssi)

        rsrp = safe_float(data.get('RSRP'))
        if rsrp is not None:
            cellwan_primary_rsrp.labels(band=band, cell_id=cell_id, enodeb_id=enodeb_id).set(rsrp)

        rsrq = safe_float(data.get('RSRQ'))
        if rsrq is not None:
            cellwan_primary_rsrq.labels(band=band, cell_id=cell_id, enodeb_id=enodeb_id).set(rsrq)

        sinr = safe_float(data.get('SINR'))
        if sinr is not None:
            cellwan_primary_sinr.labels(band=band, cell_id=cell_id, enodeb_id=enodeb_id).set(sinr)

        cqi = safe_int(data.get('CQI'))
        if cqi is not None:
            cellwan_primary_cqi.labels(band=band, cell_id=cell_id, enodeb_id=enodeb_id).set(cqi)

        mcs = safe_int(data.get('MCS'))
        if mcs is not None:
            cellwan_primary_mcs.labels(band=band, cell_id=cell_id, enodeb_id=enodeb_id).set(mcs)

        ri = safe_int(data.get('RI'))
        if ri is not None:
            cellwan_primary_ri.labels(band=band, cell_id=cell_id, enodeb_id=enodeb_id).set(ri)

        pmi = safe_int(data.get('PMI'))
        if pmi is not None:
            cellwan_primary_pmi.labels(band=band, cell_id=cell_id, enodeb_id=enodeb_id).set(pmi)

        ul_bw = safe_float(data.get('UL Bandwidth (MHz)'))
        if ul_bw is not None:
            cellwan_primary_bandwidth_ul.labels(band=band, cell_id=cell_id, enodeb_id=enodeb_id).set(ul_bw)

        dl_bw = safe_float(data.get('DL Bandwidth (MHz)'))
        if dl_bw is not None:
            cellwan_primary_bandwidth_dl.labels(band=band, cell_id=cell_id, enodeb_id=enodeb_id).set(dl_bw)

        phy_cell_id = safe_int(data.get('Physical Cell ID'))
        if phy_cell_id is not None:
            cellwan_primary_physical_cell_id.labels(band=band, cell_id=cell_id, enodeb_id=enodeb_id).set(phy_cell_id)

        rfcn = safe_int(data.get('RFCN'))
        if rfcn is not None:
            cellwan_primary_rfcn.labels(band=band, cell_id=cell_id, enodeb_id=enodeb_id).set(rfcn)

        # NR5G metrics
        if 'nr5g' in data and data['nr5g']:
            nr5g = data['nr5g']
            nr5g_band = nr5g.get('Band', 'unknown')
            mcc = nr5g.get('MCC', 'unknown')
            mnc = nr5g.get('NNC', 'unknown')

            nr5g_rsrp = safe_float(nr5g.get('RSRP'))
            if nr5g_rsrp is not None:
                cellwan_nr5g_rsrp.labels(band=nr5g_band, mcc=mcc, mnc=mnc).set(nr5g_rsrp)

            nr5g_rsrq = safe_float(nr5g.get('RSRQ'))
            if nr5g_rsrq is not None:
                cellwan_nr5g_rsrq.labels(band=nr5g_band, mcc=mcc, mnc=mnc).set(nr5g_rsrq)

            nr5g_sinr = safe_float(nr5g.get('SINR'))
            if nr5g_sinr is not None:
                cellwan_nr5g_sinr.labels(band=nr5g_band, mcc=mcc, mnc=mnc).set(nr5g_sinr)

            nr5g_dl_bw = safe_float(nr5g.get('DL Bandwidth (MHz)'))
            if nr5g_dl_bw is not None:
                cellwan_nr5g_bandwidth_dl.labels(band=nr5g_band, mcc=mcc, mnc=mnc).set(nr5g_dl_bw)

            nr5g_phy_cell = safe_int(nr5g.get('Physical Cell ID'))
            if nr5g_phy_cell is not None:
                cellwan_nr5g_physical_cell_id.labels(band=nr5g_band, mcc=mcc, mnc=mnc).set(nr5g_phy_cell)

            nr5g_rfcn = safe_int(nr5g.get('RFCN'))
            if nr5g_rfcn is not None:
                cellwan_nr5g_rfcn.labels(band=nr5g_band, mcc=mcc, mnc=mnc).set(nr5g_rfcn)

        # SCC metrics
        if 'scc' in data:
            for scc_idx, scc_info in data['scc'].items():
                if not scc_info:
                    continue

                scc_band = scc_info.get('Band', 'unknown')
                scc_phy_cell = scc_info.get('Physical Cell ID', 'unknown')

                scc_rssi = safe_float(scc_info.get('RSSI'))
                if scc_rssi is not None:
                    cellwan_scc_rssi.labels(scc_index=scc_idx, band=scc_band, physical_cell_id=scc_phy_cell).set(scc_rssi)

                scc_rsrp = safe_float(scc_info.get('RSRP'))
                if scc_rsrp is not None:
                    cellwan_scc_rsrp.labels(scc_index=scc_idx, band=scc_band, physical_cell_id=scc_phy_cell).set(scc_rsrp)

                scc_rsrq = safe_float(scc_info.get('RSRQ'))
                if scc_rsrq is not None:
                    cellwan_scc_rsrq.labels(scc_index=scc_idx, band=scc_band, physical_cell_id=scc_phy_cell).set(scc_rsrq)

                scc_sinr = safe_float(scc_info.get('SINR'))
                if scc_sinr is not None:
                    cellwan_scc_sinr.labels(scc_index=scc_idx, band=scc_band, physical_cell_id=scc_phy_cell).set(scc_sinr)

                scc_dl_bw = safe_float(scc_info.get('DownlinkBandwidth (MHZ)'))
                if scc_dl_bw is not None:
                    cellwan_scc_bandwidth_dl.labels(scc_index=scc_idx, band=scc_band, physical_cell_id=scc_phy_cell).set(scc_dl_bw)

                scc_rfcn = safe_int(scc_info.get('RFCN'))
                if scc_rfcn is not None:
                    cellwan_scc_rfcn.labels(scc_index=scc_idx, band=scc_band, physical_cell_id=scc_phy_cell).set(scc_rfcn)

        # Neighbor metrics
        if 'neighbors' in data:
            for neighbor in data['neighbors']:
                idx = neighbor.get('index', 'unknown')
                ntype = neighbor.get('type', 'unknown')
                mode = neighbor.get('mode', 'unknown')
                phy_cell = neighbor.get('physical_cell_id', 'unknown')
                rfcn = neighbor.get('rfcn', 'unknown')

                n_rssi = safe_float(neighbor.get('rssi'))
                if n_rssi is not None:
                    cellwan_neighbor_rssi.labels(neighbor_index=idx, neighbor_type=ntype, mode=mode,
                                                physical_cell_id=phy_cell, rfcn=rfcn).set(n_rssi)

                n_rsrp = safe_float(neighbor.get('rsrp'))
                if n_rsrp is not None:
                    cellwan_neighbor_rsrp.labels(neighbor_index=idx, neighbor_type=ntype, mode=mode,
                                                physical_cell_id=phy_cell, rfcn=rfcn).set(n_rsrp)

                n_rsrq = safe_float(neighbor.get('rsrq'))
                if n_rsrq is not None:
                    cellwan_neighbor_rsrq.labels(neighbor_index=idx, neighbor_type=ntype, mode=mode,
                                                physical_cell_id=phy_cell, rfcn=rfcn).set(n_rsrq)


def fetch_cellwan_status(host, user, password):
    """Fetch cellwan_status via SSH"""
    try:
        cmd = [
            'sshpass',
            '-p',
            password,
            'ssh',
            '-tt',
            '-o',
            'StrictHostKeyChecking=no',
            '-o',
            'UserKnownHostsFile=/dev/null',
            '-o',
            'LogLevel=ERROR',
            '-o',
            'ConnectTimeout=10',
            f'{user}@{host}',
        ]
        logger.debug(f"Executing SSH command to {host}...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            input='cfg cellwan_status get\nexit\n',
            text=True,
            timeout=15,
            check=False,
        )

        if result.returncode == 0:
            logger.debug(f"SSH command successful, received {len(result.stdout)} bytes")
            return result.stdout.replace('\r', '')
        else:
            logger.error(f"SSH command failed with return code {result.returncode}")
            logger.debug(f"STDERR: {result.stderr}")
            logger.debug(f"STDOUT: {result.stdout}")
            return None
    except subprocess.TimeoutExpired as e:
        logger.error(f"SSH command timed out after {e.timeout}s")
        logger.debug(f"Command: sshpass ssh ... {user}@{host} 'cfg cellwan_status get'")
        return None
    except Exception as e:
        logger.error(f"Exception during SSH: {type(e).__name__}: {e}")
        return None


def collect_metrics(host, user, password, interval):
    """Continuously collect metrics at specified interval"""
    logger.info(f"Starting metric collection every {interval} seconds...")

    while True:
        try:
            output = fetch_cellwan_status(host, user, password)
            if output:
                data = parse_cellwan_status(output)
                update_metrics(data)
                logger.info("Metrics updated successfully")
            else:
                logger.warning("Failed to fetch data")
                mark_scrape_failed()
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            mark_scrape_failed()

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(
        description='Zyxel 5G Router Prometheus Exporter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using command line arguments
  %(prog)s --host 192.168.1.1 --user admin --password secret --interval 30

  # Using environment variables or .env file
  export ZYXEL_HOST=192.168.1.1
  export ZYXEL_USER=admin
  export ZYXEL_PASSWORD=secret
  %(prog)s

  # Custom exporter port and IP
  %(prog)s --host 192.168.1.1 --user admin --password secret --port 9100 --listen 0.0.0.0

Environment variables (can also be set in .env file):
  ZYXEL_HOST       - Router IP address or hostname
  ZYXEL_USER       - SSH username
  ZYXEL_PASSWORD   - SSH password
  EXPORTER_PORT    - Prometheus exporter port (default: 9101)
  EXPORTER_IP      - IP to bind exporter (default: 0.0.0.0)
  SCRAPE_INTERVAL  - Seconds between scrapes (default: 30)
  DEBUG            - Enable debug output (true/false, default: false)
        """
    )
    
    parser.add_argument('--host', help='Router hostname or IP address')
    parser.add_argument('--user', help='SSH username')
    parser.add_argument('--password', help='SSH password')
    parser.add_argument('--port', type=int, default=int(os.getenv('EXPORTER_PORT', 9101)),
                       help='Prometheus exporter port (default: 9101)')
    parser.add_argument('--listen', default=os.getenv('EXPORTER_IP', '0.0.0.0'),
                       help='IP address to bind exporter (default: 0.0.0.0)')
    parser.add_argument('--interval', type=int, default=int(os.getenv('SCRAPE_INTERVAL', 30)),
                       help='Scrape interval in seconds (default: 30)')
    
    args = parser.parse_args()
    
    # Get credentials from args or environment
    host = args.host or os.getenv('ZYXEL_HOST')
    user = args.user or os.getenv('ZYXEL_USER')
    password = args.password or os.getenv('ZYXEL_PASSWORD')
    
    # Validate required parameters
    if not all([host, user, password]):
        parser.error('Host, user, and password must be provided via arguments or environment variables')

    # Start Prometheus HTTP server
    logger.info(f"Starting Prometheus exporter on {args.listen}:{args.port}")
    start_http_server(args.port, addr=args.listen)
    logger.info(f"zyxel_cellwan_exporter listening on {args.listen}:{args.port}")

    # Start metric collection
    try:
        collect_metrics(host, user, password, args.interval)
    except KeyboardInterrupt:
        logger.info("Exporter stopped by user")
        sys.exit(0)


if __name__ == '__main__':
    main()
