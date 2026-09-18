# FC5K

The Freezing Cold 5K. Elmhurst, Illinois. December 26.
Perpetual trophy: the Frozen Icicle of Glory.

Site: [fc5k.org](https://fc5k.org) (target)  
Repo: [github.com/zachback64/fc5k](https://github.com/zachback64/fc5k)

## Status

Public clubhouse site. Year eight was Ocho (2025). Next is Nueve: Saturday, December 26, 2026.

Course: Zach’s → Jack’s → Kayla’s and back.
Gather 2pm (hot chocolate and schnapps). Gun at 3.

## Local

This is a static site. Open `index.html` or serve the repo root.

## GitHub Pages

1. Repo → Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` / root
4. After it builds, temporary URL: `https://zachback64.github.io/fc5k/`

## Domain (fc5k.org)

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
