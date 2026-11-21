# Gentle website

A static site for Gentle, built to be hosted free on GitHub Pages like Write as Rain.

## Editing a page

Each page's words live in `src/pages/<page>.html`. The top of each file has a short header:

```
---
title: The title shown in Google and the browser tab
description: The snippet under it in Google (aim for 140 to 155 characters)
crumb: The short name used in breadcrumbs and the footer
blurb: One line used when other pages link here under "Related pages"
related: other-page.html, another-page.html
---
```

Everything else on the page (header, theme picker, the promise band, footer, search tags) is added by the build.

FAQ blocks are written like this, and the build turns them into Google's FAQ schema automatically:

```html
<details class="faq-item">
  <summary>The question?</summary>
  <div><p>The answer.</p></div>
</details>
```

## Building

```
python website/scripts/build.py
```

This writes every page to the site root, plus `sitemap.xml`, `robots.txt` and `llms.txt` (from `src/`). It also checks the wording against the house rules (words like "delve" or "seamless", em dashes, "in summary") and warns about titles or descriptions that are too long.

Two settings at the top of `scripts/build.py`:

- `SITE`: the site's address, `https://gentle-app.github.io/`. Change it once (for example to your own domain) and every page, the sitemap, `robots.txt` and `llms.txt` follow.
- `HEAD_EXTRA`: paste the GA4 and Clarity tags here when they're set up. They go in every page's `<head>`. Add a cookie notice and update the privacy page at the same time.

`scripts/build-images.ps1` redraws `apple-touch-icon.png` and `og-image.png` (the picture shown when the site is shared).

## Screenshots

The app screenshots in `img/app/` are real, taken from Gentle's sample data in the Android emulator. The full-size originals are in `Gentle/screenshots/raw/` (named `raw-<name>.png`, 1080 x 2400).

`python website/scripts/clean_screenshots.py` (needs Pillow) turns the originals into the website images. It replaces the status bar strip at the top with plain background, because the website draws its own tidy status bar and camera over that strip, and it saves 600-pixel-wide JPEGs. Today screens are cropped to start at the points card. The build reads each image's real size, so pages never need their width and height editing by hand.

In the page source, a screenshot is just `<div class="phone"><img ...></div>` (or `phone phone-sm` for the smaller size). The build wraps it in the phone frame.

Still to add, because the emulator crashes drawing these themes:

- `today-y2k` and `today-aero`: the Today screen in Y2K sparkle and Frutiger Aero, scrolled the same as the other Today screenshots. Save them as `raw-today-y2k.png` and `raw-today-aero.png` and run the script. A screenshot from a phone that isn't 1080 x 2400 may need the crop numbers in the script adjusting. Then replace the two `shot-slot` boxes in `src/pages/themes.html` with images, and point `y2k` and `aero` at them in `site.js`.
- A screenshot of the Gentle watch app, for the watches page.

## The comparison table

`src/pages/free-no-subscription.html` compares Gentle with Visible and FatigueSense. Each fact was checked on 21 November 2026 against the apps' own websites, help pages and App Store listings. FatigueSense's £5.99 a month came from the developer. Check the table again before publishing and every few months after that, and change the "Checked on" date when you do.

## Publishing on GitHub Pages

The site is live at <https://gentle-app.github.io/>, published from the repository [Gentle-App/Gentle-App.github.io](https://github.com/Gentle-App/Gentle-App.github.io) (21 November 2026). A GitHub organisation's own Pages site has to live in a repository named `<organisation>.github.io`, which is why the address is gentle-app rather than gentle. The name `gentle.github.io` belongs to someone else's account.

To publish changes, edit the pages in `src/`, then run:

```
python website/scripts/deploy.py "What changed"
```

It builds the site, copies it into a separate copy of the repository in `%LOCALAPPDATA%\GentlePages` (so there's no git in the Gentle project folder), and pushes. GitHub republishes within a minute or two. It needs git and a GitHub sign-in that can push to Gentle-App (`gh auth login`).

To use your own domain later: add it under the repository's Settings, then Pages, point the domain's DNS at GitHub, and change `SITE` in `scripts/build.py`.

After publishing, add the site to Google Search Console and submit `sitemap.xml`.
