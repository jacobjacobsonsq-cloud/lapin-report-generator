# Lapin Website Setup (Free Hosting)

Goal: make `calebgoodman.com/lapin` work with no paid Railway plan.

## 1) Publish this LAPIN project to GitHub

From this folder:

```bash
cd /Users/calebgoodman/Documents/coding/LAPIN
git init
git add .
git commit -m "prepare LAPIN for cloud deploy"
```

Create an empty GitHub repo (for example `lapin-report-generator`), then connect and push:

```bash
git remote add origin git@github.com:<your-username>/lapin-report-generator.git
git branch -M main
git push -u origin main
```

## 2) Deploy on Streamlit Community Cloud (free)

1. Go to `https://share.streamlit.io/` and sign in with GitHub.
2. Click **Create app**.
3. Repository: `lapin-report-generator` (or your chosen name).
4. Branch: `main`.
5. Main file path: `app.py`.
6. Deploy.

After deploy, you will get a URL like:

`https://<your-app-name>.streamlit.app`

## 3) Wire `/lapin` on your website

In your Vercel project for `calebgoodman.com`, set:

- `NEXT_PUBLIC_LAPIN_EMBED_URL=https://<your-app-name>.streamlit.app`

Then redeploy production.

## 4) Result

- `calebgoodman.com/lapin` works.
- No visible nav link is required.
- Only people with the direct URL can find it normally.
