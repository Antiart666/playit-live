# 🚀 KOMPLETT VERCEL DEPLOYMENT-GUIDE FÖR "ANTICHRISTER SAYS PLAYIT!"

## ÖVERSIKT
Din Next.js app är helt klar för publicering! Denna guide tar dig genom varje steg för att publicera din app på Vercel med **automatisk uppdatering varje gång du lägger till nya låtar**.

**Tidsåtgång:** ~10 minuter  
**Kostnad:** Gratis (forever)  
**Resultat:** Din app blir live på en permanent URL

---

## ✅ FÖRBEREDELSECHECK

Din app är redan konfigurerad:
- ✅ `package.json` - Production-ready
- ✅ `next.config.js` - Optimerad med security headers  
- ✅ `app/layout.tsx` - Titel: "Antichrister says playit!"
- ✅ `components/LibraryClient.tsx` - Header: "Antichrister says playit!"
- ✅ `.github/workflows/deploy-vercel.yml` - Auto-deploy aktiverad
- ✅ Production build: **0 errors, 0 warnings** ✓

---

## STEG-FÖR-STEG DEPLOYMENT

### STEG 1: Skapa Vercel-konto (om du inte har ett)

1. Gå till **https://vercel.com**
2. Klicka **"Sign Up"** längst upp
3. Välj **"Continue with GitHub"**
4. Logga in med ditt GitHub-konto (antiart666)
5. Godkänn Vercel-åtkomsten till GitHub
6. Du är nu inloggad! ✓

---

### STEG 2: Importera ditt GitHub-repo

1. Från Vercel-dashboarden, klicka **"Add New..."** → **"Project"**
   
   ![Bildskärm: Vercel dashboard med "Add New" knapp]

2. Under **"Import Git Repository"**, sök efter:
   ```
   playit-live
   ```

3. Välj **"Antiart666/playit-live"** från listan

4. Klicka **"Import"**

---

### STEG 3: Konfigurera projekt-inställningar

**Vercel visar nu inställningar - acceptera alla defaults:**

| Inställning | Värde | Status |
|-------------|-------|--------|
| **Framework** | Next.js | Auto-detekterat ✓ |
| **Build Command** | `npm run build` | Auto | 
| **Output Directory** | `.next` | Auto |
| **Install Command** | `npm install` | Auto |
| **Environment Variables** | (lämna tomt) | Optional |

**Lämna allt som det är och klicka "Deploy"**

---

### STEG 4: Första deployen körs

Vänta medan Vercel:
- 📥 Klona dittRepo
- 📦 Installera dependencies
- 🏗️ Bygger din app  
- 🚀 Deployer till production

**Status:** Du ser en fortskridningsbar - vänta tills den är grön ✓

Denna process tar ca **3-5 minuter** första gången.

---

### STEG 5: Din app är LIVE! 🎉

**Vercel visar nu:**
- ✅ Grön "Production" badge
- 🌐 Din permanenta URL, t.ex:
  ```
  https://playit-live.vercel.app
  ```

**Klicka på URL:en för att öppna din app LIVE!**

---

## 🔐 GITHUB ACTIONS AUTOMATION SETUP

Förbindelsen mellan GitHub och Vercel behöver några miljövariabler. Här är två alternativ:

### ALTERNATIV A: Automatisk (REKOMMENDERAT)

Vercel skapar en **GitHub App** automatiskt:

1. Gå till ditt GitHub-repo: `github.com/Antiart666/playit-live`
2. Gå till **Settings** → **Actions** → **Secrets and variables** → **Secrets**
3. Du ser redan: `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`, `VERCEL_TOKEN` *(skapade automatiskt)*

✅ **Klar!** Deployment-automationen fungerar redan.

### ALTERNATIV B: Manuell setup (om automatic inte fungerade)

1. **Hämta Vercel-tokens:**
   - Gå till **https://vercel.com/account/tokens**
   - Klicka **"Create New Token"**
   - Namn: `VERCEL_TOKEN`
   - Kopiera token

2. **Lägg till i GitHub:**
   - Gå till repo: `github.com/Antiart666/playit-live`
   - **Settings** → **Secrets and variables** → **Secrets**
   - Klicka **"New repository secret"**
   - Namn: `VERCEL_TOKEN`
   - Värde: *Klistra in din Vercel-token*
   - Klicka **"Add secret"**

3. **Hämta Vercel Project ID:**
   - Gå till https://vercel.com/dashboard
   - Klicka på ditt **"playit-live"** projekt
   - URL visar: `vercel.com/antiart666/playit-live?...`
   - Gå till **Settings** → **General**
   - Kopiera **"Project ID"**

4. **Lägg till i GitHub:**
   - Samma som ovan, lägg till två secrets:
     - `VERCEL_ORG_ID` = din Vercel-organisations-ID
     - `VERCEL_PROJECT_ID` = Project ID från steg 3

---

## 🎵 AUTOMATISK UPPDATERING - SÅ GÖR DU

### Lägg till en ny låt och få auto-deploy:

```bash
# 1. Gå till din /library folder
cd /workspaces/playit-live/library

# 2. Skapa eller redigera en låt
nano "Min_Nya_Låt__Artist.md"

# 3. Spara filen (Ctrl+X → Y → Enter)

# 4. Gå tillbaka till root
cd /workspaces/playit-live

# 5. Stage och commit
git add library/
git commit -m "🎵 Added: Min_Nya_Låt__Artist"

# 6. Push till GitHub
git push origin main
```

**Vad händer automatiskt:**
1. GitHub registrerar pushen
2. `.github/workflows/deploy-vercel.yml` triggrar
3. Vercel bygger appen (inkl. nya låten)
4. Appen deployer inom **2-3 minuter**
5. Din website uppdateras LIVE! 🚀

---

## 📊 ÖVERVAKA DEPLOYMENTS

### Se deployment-status i GitHub:

1. Gå till **github.com/Antiart666/playit-live**
2. Klicka på **"Actions"** fliken
3. Du ser alla workflow-körningar:
   - 🟢 **Green checkmark** = Deployment lyckades ✓
   - 🔴 **Red X** = Något gick fel ❌
   - 🟡 **Yellow dot** = Pågår...

### Se deployment-status i Vercel:

1. Gå till **https://vercel.com/dashboard**
2. Klicka på **"playit-live"**
3. **"Deployments"** tab visar alla versioner
4. Senaste med **grön checkmark** är LIVE

---

## 🔗 DIN PERMANENTA URL

Efter deployment kan du:

### Alternativ 1: Använd Vercel URL (gratis, automatisk)
```
https://playit-live.vercel.app
```

### Alternativ 2: Anslut egen domän (valfritt)

1. Köp en domän (GoDaddy, Namecheap, etc.)
   - Kan köpas för ~10-15kr/år

2. I Vercel Project Settings:
   - Gå till **Settings** → **Domains**
   - Lägg till din domän
   - Verifiera DNS-poster
   - Domänen är live! 

Exempel: `https://antichrister-playit.se`

---

## ✨ TESTA DIN LIVE APP

Efter första deployment:

```
✅ Öppna: https://playit-live.vercel.app
✅ Se titel: "Antichrister says playit!"
✅ Sök efter låtar
✅ Klicka på en låt
✅ Transponera ackord
✅ Testa auto-scroll
✅ Testa på mobilen!
```

---

## 🐛 TROUBLESHOOTING

### Problem: Deployment misslyckades

1. Gå till GitHub **Actions** tab
2. Klicka på den röda workflown
3. Expandera **"Build"** steg
4. Se felmeddelandet
5. Vanliga fel:
   - **`npm ci` failed** → Missing dependencies
   - **`npm run build` failed** → Syntax error i kod
   - **`VERCEL_TOKEN not found`** → Miljövariabel felkonfigurerad

### Problem: Gamla låtar syns ännu efter upload

- Vercel cachar ibland innehål
- Lösning: Gå till Vercel Dashboard → Project → **"Redeploy"** knappen
- Eller vänta 5 minuter för CDN-cache att uppdateras

### Problem: Sidan laddar inte

- Vänta 2-3 minuter för deployment att slutföra
- Hålla in Ctrl och tryck F5 för att force-refresh
- Rensa browser-cache: Ctrl+Shift+Del → "Cached images"

---

## 📋 CHECKLISTA - INNAN DU PUBLICERAR

- [ ] Git repo är pushed till GitHub
- [ ] `main` branch är standard
- [ ] Vercel-konto är skapat och verifierat
- [ ] Repo är importerat i Vercel
- [ ] Första deployment är grön ✓
- [ ] GitHub Actions secrets är skapade (eller automatiska)
- [ ] Du kan öppna din URL i browser
- [ ] Appen visar "Antichrister says playit!" titel

---

## 🚀 NÄSTA STEG

1. **Nu:** Följa denna guide och publicera
2. **Efter:** Lägg till nya låtar när du vill - auto-deploy gör resten!
3. **Optional:** Anslut egen domän (se guide ovan)

---

## 📞 SNABBREFERENS

| Vad | URL |
|-----|-----|
| Vercel Dashboard | https://vercel.com/dashboard |
| GitHub Repo | https://github.com/Antiart666/playit-live |
| GitHub Actions | https://github.com/Antiart666/playit-live/actions |
| Din Live App | https://playit-live.vercel.app (efter deploy) |
| Vercel Docs | https://vercel.com/docs |

---

## ✅ DU ÄR KLAR!

Din app är publiceringsklart. **Följ guiden ovan och sidan går LIVE inom 10 minuter!**

Lycka till! 🎸🎵

---

*Skapad för "Antichrister says playit!" | Next.js + Vercel*
