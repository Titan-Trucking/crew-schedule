# Crew Schedule

Read-only crew schedule page with PIN access. Hosted on GitHub Pages.

## How employees get in
1. First visit: enter the crew PIN, pick their name, make a personal 4 to 6 digit PIN.
2. After that, that phone asks only for their personal PIN.
3. **Forgot PIN?** clears the phone so they start over with the crew PIN.
4. Five wrong personal PINs also clears the phone.

Personal PINs live only on that phone. A new phone or browser means setting up again.

## Admin (admin.html)
Open `/admin.html` on the live site.
- **Reset PIN**: that person's phone asks for the crew PIN again and they make a new personal PIN.
- **Revoke**: signs the person out and hides their name. To fully lock someone out, also change the crew PIN, since anyone with it can still open the page.
- **Restore**: undoes a revoke.
- **Set crew PIN**: signs out every phone.

Changes only apply after saving: tap Copy, open `config.json` on GitHub, paste over everything, Commit changes.
Phones pick up the change the next time they open the page (GitHub may take a few minutes to update).

## Files
- `index.html` - the page employees open
- `admin.html` - admin tools
- `config.json` - crew PIN, resets and revoked names
- `schedule.json` - schedule data (names, dates, times, job, truck unit only)
- `tools/export.py` - builds `schedule.json` from the scheduling board's data

## Notes
- The PIN screens keep casual visitors out. The data files themselves are not encrypted.
