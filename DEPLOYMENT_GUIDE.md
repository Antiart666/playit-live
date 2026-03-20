# 🚀 PUBLICERINGS- OCH DRIFTSÄTTNINGSGUIDE

## Automatisk uppdatering när du lägger till låtar

Din app är nu konfigurerad för automatisk publicering! Här är två alternativ:

---

## **ALTERNATIV 1: Vercel (REKOMMENDERAT för Next.js)**

Vercel är optimerat för Next.js och erbjuder:
- ✅ Gratis hosting
- ✅ Automatiska deployments
- ✅ Integrerad CDN
- ✅ Miljövariabler støtte för alla filer

### Setup:
1. Gå till https://vercel.com och skapa ett konto
2. Koppla ditt GitHub-repo
3. Vercel guider dig genom inställningarna
4. OAuth tokens skapas automatiskt

Sedan, **varje gång du pushar till `main`**:
```bash
git add library/
git commit -m "Added new song: ..."
git push origin main
```

→ GitHub Action körs automatiskt → App uppdateras på din Vercel-URL

**Dina hemsidans URL blir något som:** `https://antichrister-playit.vercel.app`

---

## **ALTERNATIV 2: GitHub Pages (GRATIS, helt kostnadsfritt)**

GitHub Pages är helt gratis men har vissa begränsningar för CSR-appar.

### Setup:
1. Gå till din repository settings
2. Navigera till "Pages"
3. Välj "Deploy from a branch"
4. Välj `main` branch och `/root` folder

→ Varje push till `main` → deploy.yml workflow körs → App uppdateras

**Dina hemsidans URL blir:** `https://antiart666.github.io/playit-live`

---

## **WORKFLOW AUTOMATISERNING**

### När ska deployment trigga?
- 🎵 Nya låtar läggs till `/library`
- ✏️ Komponenter uppdateras i `/components`
- 🎨 Stilar ändras i `/app` eller CSS-filer
- 📝 `package.json` uppdateras (beroenden)

### Hur uppdaterar du?

```bash
# 1. Lägg till en ny låt (eller redigera befintlig)
nano library/Min_Ny_Låt.md

# 2. Spara och commit
git add library/
git commit -m "Added song: Min Ny Låt"

# 3. Push till GitHub
git push origin main

# 4. Workflow startar automatiskt!
# Binnen 2-5 minuter är din app uppdaterad live
```

---

## **STATUS OCH DEBUG**

### Se deployment-status:
- Gå till GitHub repo → "Actions" tab
- Där ser du alla workflow-körningar
- Grön checkmark = Lyckad deploy ✅
- Röd X = Något gick fel ❌

### Om något misslyckades:
1. Klicka på den röda workflown
2. Expandera "Build" steget
3. Se vad felet är
4. Fixa det lokalt och push igen

---

## **MER INFO**

- [Vercel Docs](https://vercel.com/docs)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Next.js Deployment](https://nextjs.org/learn-pages-router/basics/deploying-nextjs-app/deploy)

---

## **SAMMANFATTNING**

✅ **Ditt projekt är nu publiceringsklart!**

Nästa steg:
1. Välj deployment-plattform (Vercel rekommenderas)
2. Koppla GitHub-repo
3. Pushhat nya låtar → **Auto-deploy startar**
4. Din app är live med alla nya låtar! 🎵

Lycka till! 🎸
