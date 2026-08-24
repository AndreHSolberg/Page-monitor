# NFF billett-varsler

Sjekker automatisk resale.fotball.no for resale-billetter til landslagskamper,
og sender varsel på e-post og push (ntfy.sh) når det dukker opp noe.

## Oppsett – steg for steg

1. Opprett et **privat** repo på GitHub og last opp disse to filene med samme
   mappestruktur som her: `sjekk_billetter.py` og `.github/workflows/sjekk.yml`

2. Gå til **Settings → Secrets and variables → Actions** i repoet og legg inn:
   - `EPOST_AVSENDER` – din Gmail-adresse
   - `EPOST_APP_PASSORD` – app-passord fra https://myaccount.google.com/apppasswords
   - `EPOST_MOTTAKER` – adressen du vil motta varsel på
   - `NTFY_EMNE` – et unikt, hemmelig emnenavn, f.eks. `ola-nff-billetter-8k2x`

3. Gå til fanen **Actions**, velg workflowen, og trykk **Run workflow** for å teste.

4. Last ned appen **ntfy** (Android/iOS) og abonner på samme emnenavn som i `NTFY_EMNE`.

Ferdig! Sjekken kjører nå automatisk hvert 10. minutt på GitHub sine servere,
uavhengig av om PC-en din er på.
