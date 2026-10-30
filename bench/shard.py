"""Prepare one benchmark shard: a working directory whose database holds one share of the stars of one unit.

python bench/shard.py HOME MISSION UNIT SHARD NSHARDS
The shard's job is marked as already prepared, so `occulta survey run` searches exactly these stars and then stops.
"""
import json
import os
import sys

home, mission, unit, k, n = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
os.makedirs(f'{home}/data', exist_ok=True)
os.environ['OCCULTA_HOME'] = os.path.abspath(home)
from occulta import sources, survey  # noqa: E402  (survey reads OCCULTA_HOME on import)

tg = sources.unit_targets(unit) or {}
ids = sorted(tg)[k::n]
con = survey.db()
jid = f'{mission}:None:{unit}'
con.executemany('INSERT OR REPLACE INTO job VALUES (?,?,?,?,?)',
                [(f'{mission}:None:{u}', 'remote', 0, None, None) for u in sources.units(mission) if u != unit])
con.execute('INSERT OR REPLACE INTO job VALUES (?,?,?,?,?)', (jid, 'targets' if ids else 'missing', len(ids), None, None))
con.executemany('INSERT OR IGNORE INTO target(sector, tic, url) VALUES (?,?,?)', ((unit, t, tg[t]) for t in ids))
con.commit()
json.dump({"disk_cap_gb": 10, "raw_cap_gb": 2, "download_threads": 16, "workers": 4, "event_snr": 9.0, "inv_ratio": 1.2,
           "bls_snr": 10.0, "bls_sde": 9.0, "common_mode_n": 5, "plan": [{"mission": mission}]},
          open(f'{home}/config.json', 'w'), indent=1)
print(jid, 'shard', k, 'of', n, ':', len(ids), 'light curves')
