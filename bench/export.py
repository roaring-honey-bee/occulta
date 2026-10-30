"""Copy what a benchmark shard measured (targets, per-star noise, events, BLS hits, job) into a small database.

python bench/export.py HOME UNIT OUT.db
"""
import sqlite3
import sys

home, unit, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
src = sqlite3.connect(f'{home}/data/hunt.db')
d = sqlite3.connect(out)
for name, sql in src.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name IN "
                             "('target','star_sector','event','bls','job')"):
    d.execute(sql)
    rows = (src.execute('SELECT * FROM job WHERE job LIKE ?', (f'%:{unit}',)) if name == 'job' else
            src.execute(f'SELECT * FROM {name} WHERE sector=?', (unit,))).fetchall()
    if rows:
        d.executemany(f'INSERT OR IGNORE INTO {name} VALUES ({",".join("?" * len(rows[0]))})', rows)
d.commit()
for name in ('target', 'star_sector', 'event', 'bls'):
    print(name, d.execute(f'SELECT COUNT(*) FROM {name}').fetchone()[0])
print('searched', d.execute('SELECT COUNT(*) FROM target WHERE status>0').fetchone()[0])
