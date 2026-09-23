# FC5K

The Freezing Cold 5K. Elmhurst, Illinois. December 26.
Perpetual trophy: the Frozen Icicle of Glory.

Live site: [fc5k.vercel.app](https://fc5k.vercel.app)
Host dashboard: [fc5k.vercel.app/host](https://fc5k.vercel.app/host)
Custom domain: `fc5k.org` is not connected to this deployment.
Repo: [github.com/zachback64/fc5k](https://github.com/zachback64/fc5k)

## Status

Public clubhouse site. Year eight was Ocho (2025). Next is Nueve: Saturday, December 26, 2026.

Course: Glos Memorial Park → Wilder Park → Elmhurst University → Wilder’s garden path → home.
Gather 2pm (hot chocolate and schnapps). Gun at 3.

## Local

The public pages are static HTML; RSVP and host tools run on the Python server with SQLite. Python 3.9+ is required, with no third-party dependencies.

```sh
python3 scripts/dev.py
```

Open http://127.0.0.1:8766 for the site, `/rsvp` for public RSVPs, and `/host` for the host dashboard. The local launcher creates a host password in `data/private/host-password.txt` (gitignored, readable only by your user). Use the exact origin above; `localhost` is a different origin. For deployment, set a separate `FC5K_HOST_PASSWORD` outside git and run `server/app.py` directly.

- Anyone can RSVP with their name, attendance, party size, activity, and notes.
- Successful public RSVPs receive a private edit link. Save it to return on any device.
- Hosts create personalized invitations with a party-size limit and copy a ready-to-share message. No messages are automatically sent.
- The dashboard shows confirmed and tentative headcounts, unanswered invitations, declined invitations, and private notes.
- Invitation tokens are stored only as hashes. The dashboard can replace a lost link; the previous link stops working and the RSVP is preserved.
- Responses persist in `data/private/rsvp.sqlite3` (gitignored). Host sessions are stored in the database and expire after 12 hours or sign-out.
- Public signup attempts are limited to 20 per hour per IP; host login attempts are limited to 10 per 15 minutes. Limits are stored in the database, shared across instances, and use Vercel’s client IP header in production.

Run the integration checks with `python3 -m unittest discover -s tests -v`.

### Live deployment

The application is deployed to the `fc5k` project in the existing `zbackas-5858s-projects` Vercel account. A dedicated Neon database (`fc5k-rsvp`, free plan) stores production RSVPs, host sessions, and rate limits. Local development still uses SQLite. No guest records or passwords are uploaded with the source.

The production host password is saved locally in `data/private/production-host-password.txt` and configured as a sensitive Vercel environment variable. It differs from the development password.

Production settings:

- `DATABASE_URL`: provided by the Neon integration.
- `FC5K_HOST_PASSWORD`: a unique password of at least 16 characters.
- `FC5K_ORIGIN`: `https://fc5k.vercel.app`, used for origin checks and invitation links.

`api/index.py` adapts the Python handler to Vercel. `vercel.json` routes requests through its explicit public-file allowlist; the source tree and private archive cannot be downloaded. `.vercelignore` excludes local guest data, photos, credentials, and development files from deployment uploads.

To deploy an update from this linked directory:

```sh
python3 -m unittest discover -s tests -v
vercel --prod --yes
```

Vercel is also connected to the GitHub repository. Production environment variables are scoped to production; preview deployments need their own separate database and password before their APIs can run.

For a custom domain, first verify ownership and configure its Vercel DNS records. Update `FC5K_ORIGIN`, redirect the old host to the new canonical domain while preserving path and fragment, and redeploy. Keep database backups private. GitHub Pages cannot run the RSVP API.

The old `admin/` archive remains local-only. Do not serve the repository root with a generic static server on a public interface.

## Previous static-only hosting: GitHub Pages

1. Repo → Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` / root
4. After it builds, temporary URL: `https://zachback64.github.io/fc5k/`

## Previous static-only domain setup (fc5k.org)

The records below apply to GitHub Pages only. A deployment with RSVP storage must use the new application host’s DNS records instead.

`fc5k.org` is already registered at Namecheap (created 2022-07-21, expires 2027-07-21). It currently URL-forwards and does not resolve to this repo.

If that Namecheap account is yours:

1. Turn off URL redirect / forwarding
2. Add these DNS records:
   - `A` `@` → `185.199.108.153`
   - `A` `@` → `185.199.109.153`
   - `A` `@` → `185.199.110.153`
   - `A` `@` → `185.199.111.153`
   - `CNAME` `www` → `zachback64.github.io`
3. In the repo, keep the `CNAME` file (`fc5k.org`)
4. Pages → Custom domain → `fc5k.org` → enforce HTTPS

If it is not yours, either buy it from the current registrant or pick another domain (`thefc5k.org`, `frozenicicle.org`, etc.).

## Data and pages

- `data/public.json` — public-safe facts per year. Source for `history.html` and the Hall of Glory.
- `python3 scripts/build.py` — rebuilds `history.html` (public) and `admin/index.html` (private).
- `admin/`, `data/private/`, `photos/private/` are gitignored because this repo is public. They hold guest lists, posts, notes and every photo, and only exist on Zach's Mac. Open the admin page with `python3 -m http.server` then `/admin/`.
- To publish a photo: copy a JPG into `photos/public/<year>/` and rebuild.
