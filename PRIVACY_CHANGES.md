# Privacy and UI Improvements

## Changes Summary

### 🔒 Data Protection Changes

For privacy and data protection compliance, the following sensitive information has been **removed** from all metrics and dashboards:

#### Removed from Metrics:
- ❌ **IMEI** - Device identifier removed
- ❌ **Module Software Version** - Hardware/software version removed

#### Still Available (Non-sensitive):
- ✅ **Network Information** (operator, technology)
- ✅ **Access Technology** (NR5G-NSA, LTE, etc.)
- ✅ **CA Combination** (active bands)
- ✅ **Cell IDs** (tower identifiers, not device identifiers)
- ✅ **All signal metrics** (RSRP, RSSI, SINR, RSRQ, bandwidth, etc.)

### 📊 Dashboard Improvements

The Grafana dashboard has been reorganized for better clarity:

#### 1. **Datasource Selector Added**
- Dropdown selector at the top of the dashboard
- Allows switching between multiple Prometheus instances
- All panels automatically use the selected datasource

#### 2. **Grouped Metric Layout**
The dashboard is now organized into clear sections:

```
┌─────────────────────────────────────────────────┐
│ Connection Status │ Network Information         │
├─────────────────────────────────────────────────┤
│ 📡 PRIMARY LTE CELL (BC1)                       │
├─────────────────────────────────────────────────┤
│ RSRP │ RSSI │ SINR │ RSRQ │  [Signal Chart]    │
├─────────────────────────────────────────────────┤
│ 🚀 NR5G CELL (N28)                              │
├─────────────────────────────────────────────────┤
│ RSRP │ SINR │ RSRQ │ DL BW │  [Signal Chart]   │
├─────────────────────────────────────────────────┤
│ SIGNAL QUALITY COMPARISON                       │
├─────────────────────────────────────────────────┤
│ [SINR/RSRQ Chart] │ [Bandwidth Chart]          │
├─────────────────────────────────────────────────┤
│ SECONDARY CARRIERS (SCC)                        │
├─────────────────────────────────────────────────┤
│ [SCC RSRP Chart]  │ [SCC SINR Chart]           │
└─────────────────────────────────────────────────┘
```

#### 3. **Section Headers**
Each major section now has a clear header:
- **Primary LTE Cell** - Shows primary LTE metrics
- **NR5G Cell** - Shows 5G specific metrics
- **Signal Quality Comparison** - Compares LTE vs 5G
- **Secondary Carriers** - Shows all SCC metrics

#### 4. **Color-Coded Metrics**
Signal quality metrics now use thresholds:
- 🔴 **Red**: Poor signal
- 🟠 **Orange**: Fair signal
- 🟡 **Yellow**: Good signal
- 🟢 **Green**: Excellent signal

### 📝 Files Modified

1. **cellwan_exporter.py**
   - Removed IMEI from `cellwan_info` metric
   - Removed Module Software Version from `cellwan_info` metric

2. **grafana/provisioning/dashboards/cellwan.json**
   - Added datasource selector variable
   - Reorganized panels into logical sections
   - Added row headers for grouping
   - Improved stat panels with color thresholds
   - Better legend formatting with statistics

3. **README.md**
   - Updated metrics documentation
   - Removed references to IMEI and Module version

### 🔍 What Information is Still Collected?

The exporter still collects all **non-identifying** technical metrics:

**Network Metrics:**
- Network name and technology
- Cell IDs (tower identifiers, not device-specific)
- Carrier aggregation combinations

**Signal Quality Metrics:**
- RSRP (Reference Signal Received Power)
- RSSI (Received Signal Strength Indicator)
- RSRQ (Reference Signal Received Quality)
- SINR (Signal-to-Interference-plus-Noise Ratio)
- CQI (Channel Quality Indicator)
- MCS (Modulation and Coding Scheme)

**Bandwidth Metrics:**
- Uplink/Downlink bandwidth
- Per-carrier bandwidth

**Neighbor Cell Information:**
- Signal quality of nearby towers
- For handover optimization

### 🛡️ Privacy Benefits

By removing IMEI and module version:

1. **No Device Tracking**: IMEI cannot be used to track specific devices
2. **Anonymized Data**: Metrics are now fully anonymized
3. **GDPR Compliance**: Reduced personal data collection
4. **Multi-User Safe**: Safe to share dashboards without revealing device identity
5. **Public Monitoring**: Can publish dashboards publicly without privacy concerns

### 📈 Example Dashboard View

The new dashboard shows metrics grouped by cell type:

**Primary LTE Cell (BC1):**
- RSRP: -76 dBm 🟢
- RSSI: -48 dBm 🟢
- SINR: 20 dB 🟢
- RSRQ: -8 dB 🟢

**NR5G Cell (N28):**
- RSRP: -66 dBm 🟢
- SINR: 30 dB 🟢
- RSRQ: -11 dB 🟢
- DL BW: 10 MHz

This makes it immediately clear which technology (LTE vs 5G) each metric belongs to.

### 🔄 Migration Notes

If you're upgrading from a previous version:

1. **No data loss**: Historical metrics remain intact
2. **Dashboard updates**: Import the new dashboard JSON
3. **Queries still work**: All PromQL queries are compatible
4. **Info metric changed**: `cellwan_info` now has fewer labels

### ✅ Testing

To verify the changes:

```bash
# Check that IMEI is not exposed
curl http://localhost:9101/metrics | grep -i imei
# Should return nothing

# Check that info metric still works
curl http://localhost:9101/metrics | grep cellwan_info
# Should show network, access_technology, ca_combination only
```

### 📞 Support

If you have questions about these changes or need to restore removed fields for specific use cases, please open an issue on GitHub.

---

**Note**: These changes prioritize user privacy while maintaining full functionality for network monitoring and troubleshooting.
