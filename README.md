# Crew Schedule

Read-only crew schedule page with a PIN screen. Hosted on GitHub Pages.

## Files
- `index.html` - the page employees open
- `schedule.json` - the schedule data (names, dates, times, job, truck unit only)
- `config.js` - PIN settings
- `set-pin.html` - makes the code for a new PIN
- `tools/export.py` - builds `schedule.json` from the scheduling board's data

## Change the PIN
1. Open `set-pin.html` on the live site (or locally), type the new PIN, tap **Make code**.
2. Edit `config.js` on GitHub, replace the `pinHash` value and set `pinLength`.
3. Commit. Everyone is signed out and needs the new PIN.

## Notes
- The PIN screen keeps casual visitors out. The data file itself is not encrypted.
- Each phone remembers the PIN and the employee's name until they tap **Lock**.
