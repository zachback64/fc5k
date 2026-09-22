# FC5K — research notes

Background assembled from Gmail, Google Calendar, Google Drive, and Notion.
Everything here is sourced. Where a claim is unverified, it says so.

**Rule for this file: empty is better than invented.** The site already follows
this (see the Hall of Glory table). Keep it that way.

## Origin

Founded **December 26, 2018**, Elmhurst, IL. Year one collected an *optional*
$10 Venmo — "Optional Freezing Cold 5K donation for food + prizes (next year
there will be an entry fee)." Adam Greer, Kayla Spencer, and Cori Duncan paid;
Lorenzo Munoz declined.

A personal todo list from Dec 19, 2018 (subject: "HURSTIGANS") reads
"Freezing cold 5k invite nick n marc" — Nick and Marc being Zach's brothers.
It started as a hometown-friends-and-family thing and stayed that way.

## The canonical event description

From the 2023 Google Calendar entry for the 6th annual (Seis). This is the
richest surviving source of voice and detail, because the Partiful description
was pasted into the calendar event. Reproduced closely:

> Come one and all to the SIXTH ANNUAL Freezing Cold 5K!!! Holy crap we made
> it to six. For this year's event we have custom FC5K noodies available for
> all participants. This is NOT the FC5K to miss.
>
> **The Plan:** gather at the Backas House for a warming treat before the start
> gun sounds sharply at 3:00 PM. Trophies awarded for:
> - First place overall
> - Last place overall
> - and some other stuff too
>
> The course will run from the Backas House on Kenmore to Kayla/Jacqueline's
> neck of the woods by Butterfield Park back to Zach's house. It's just over
> 5k/3 miles. **This is the Official Freezing Cold 5K course.**
>
> After the race, a fun and cool party will follow. The Backas family will
> welcome racers and spectators alike with a warm fire and festive libations.
> The Backas Family Hot Tub will be fully operational and warmth + coziness
> will be provided for all. The party will include consumption of food and the
> trophies awarded.
>
> Please include noodie size in RSVP comment :) after party will start around
> 3:30pm so feel free to come even if you're not a runner!

Note the afterparty is at the house — fire, hot tub, food, trophies. Any course
redesign should keep the **finish** at the house or the party logistics break.

## Year by year

| Year | Edition | What's documented | Source |
|------|---------|-------------------|--------|
| 2018 | Uno | First running. Optional $10 donation, no merch. | Venmo, Jan 2019 |
| 2019 | Dos | — | none found |
| 2020 | Tres | Photo "2020 FC5K.JPG" exists in Drive | Drive |
| 2021 | Cuatro | Facebook event `fb.me/e/aCPyYGucM` | self-email, 12/9/21 |
| 2022 | Cinco | Partiful `XYP6AF6isvAmIzkrJes3`. **2:00 PM start.** | email to C. Kern |
| 2023 | Seis | Partiful `SZMg99cspm5KRotLiSkx`. 3:00 PM gun. "Noodies." | Calendar |
| 2024 | Siete | Merch inquiry to Rowboat Creative, Nov 2024 | Gmail |
| 2025 | Ocho | 10 went / 6 maybe (per existing site) | site |
| 2026 | Nueve | Sat Dec 26 — upcoming | — |

Note the **start time moved from 2:00 PM (2022) to 3:00 PM (2023)**.

## Merch history

- **2022 (Cinco)** — $30/shirt. Vendor: One Hour Tees (Cailey Wagner).
  Designed with Jack Corry; there was a "FC5K t shirt review" video call.
  Bella+Canvas ladies fitted long sleeve Athletic Heather, and Next Level in
  Heather Grey. Women's tees went out of stock; order swapped to unisex.
- **2023 (Seis)** — "noodies," ~$20. Size collected in the Partiful RSVP.
- **2024 (Siete)** — quoted by Rowboat Creative. A Google Doc titled
  "7th FC5K t shirt" exists in Drive but is image-only (7.6 MB, no extractable
  text) — needs to be read as an image.

**Merch buyers across years** (rough participant roster): Jack Corry, Kayla
Spencer, Marc Backas, Morgan Semmelhack, Kelly Nikitas, Rebecca Papineau,
Jacob Ruprecht, Jenna Klewicki, Tyler Sill, Adam Greer, Matt Shulda.

Tyler Sill paid $20.01 for his "Nood Shirt."

## Other assets

- Instagram: **@freezingcold5k**
- Google Drive folder "FC5K" — "2018 FC5K.JPG", "2020 FC5K.JPG", and a batch
  of photos from Sept 2024.
- Chris Kern (`ckern@elmhurst205.org`, Elmhurst District 205) was invited in
  2022 — the invite list reaches beyond the immediate friend group.

## Open questions / unverified

1. **The course line on the site** currently reads "Zach's → Jack's → Kayla's
   and back." The only primary source found (2023 calendar) says Backas House
   on Kenmore → Kayla/Jacqueline's by Butterfield Park → back, with **no Jack's
   leg**. Unresolved. Moot if the 2026 course moves to Wilder Park.
2. **"The Frozen Icicle of Glory"** appears in this repo's README but in no
   other source found. Likely true, just undocumented elsewhere.
3. **Hall of Glory winners** — no record found for any year. The 2023 event
   text confirms trophies for first and last place, but names no winners.
4. **"Do I have to run?"** — the FAQ answer lives only on Partiful and has not
   been recovered. `index.html` is holding a slot for it.
5. **Backas house number on Kenmore** — needed to anchor any course.

## Data sources: what worked and what didn't

- **Gmail** — productive. Note `from:partiful.com` returns **zero** messages
  across the entire mailbox including trash/spam. Partiful is SMS-first, so no
  invite bodies, RSVPs, or guest lists ever reached email. Don't re-run that
  search expecting different results.
- **Google Calendar** — one entry (2023), but it's the single best source.
- **Google Drive** — photos and the image-only shirt doc.
- **Notion** — see below.
- **Apple Notes** — no connector exists. Local to the Mac/iCloud. Only readable
  from a Claude Code session running *on that Mac*.
- **Facebook / Partiful** — no connectors. Both domains blocked by the cloud
  environment's egress proxy. OpenStreetMap and Overpass are blocked too, which
  is why the Wilder Park course could not be measured.

## Notion cleanup (done 2026-09-18)

The Portfolio Projects database had FC5K described as *"Formula Kite 5000 — a
high-performance kitefoil racing regatta on San Francisco Bay."* Entirely
fabricated. Root cause: the **Kiteracing** page listed "FC5K" among
IKA-sanctioned regattas alongside the Belmont Kite Classic, and the FC5K page
was generated to match.

- Fixed the FC5K page description; set `Year: 2025`.
- Removed FC5K from the Kiteracing regatta list.

**Still outstanding:**
- The 8 images at `/images/fc5k/01–08.jpg` may be kitefoil photos chosen to
  match the false description. Needs a human eyeball.
- A **duplicate** blank FC5K page (`Category: photography`, also
  `Published: YES`, also slug `fc5k`) sits under *Zuzu's Petals Ops Manual →
  Admin & Misc → Key Contacts & Codes → Portfolio Projects*. Two published
  pages with the same slug will collide on the portfolio site.
- `fc5k.org` still URL-forwards and does not resolve to this repo, so no link
  was added to the portfolio page yet.
