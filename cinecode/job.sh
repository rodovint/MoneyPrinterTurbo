#!/usr/bin/env bash
# Job 28 (2026-11-15): escudos que faltaron (Commons, con pausas)
set -u
O=cinecode/out; mkdir -p $O
python3 cinecode/escudos.py $O/escudos '{
 "macara": ["Macará Ambato escudo", "Club Social y Deportivo Macará"],
 "orense": ["Orense Sporting Club escudo", "Orense SC Machala"],
 "mushuc": ["Mushuc Runa escudo", "Mushuc Runa Sporting Club"],
 "aucas": ["Aucas escudo", "Sociedad Deportiva Aucas"],
 "cuenca": ["Deportivo Cuenca escudo", "Club Deportivo Cuenca Ecuador"],
 "manta": ["Manta FC escudo", "Manta Fútbol Club Ecuador"],
 "delfin": ["Delfín SC escudo", "Delfín Sporting Club Manta"]
}' 2>&1 | tail -60
