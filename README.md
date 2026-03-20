# PlayIt! Pro - Next.js Migration Guide

## 🎵 Welcome to PlayIt! 2.0

Your music transposition app has been successfully migrated from Streamlit to **Next.js + Material Design 3**. This guide will help you get started.

---

## ⚡ Quick Start

### 1. Install Dependencies (already done ✅)
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```
- Opens at **http://localhost:3000**
- Hot Module Reload (HMR) enabled for instant changes
- Server ready in ~2 seconds

### 3. Build for Production
```bash
npm run build
npm start
```

---

## 🎯 How the App Works

### Library View (Landing Page)
- Shows all songs from `/library/*.md` files
- Click any song to open it
- Responsive button grid

### Song View
- Displays lyrics with chords highlighted in **purple (#D187FF)**
- Sticky header with logo (top-left)
- Floating control panel (bottom-right)

### Controls

#### Tone Adjustment
```
[−]  Transpose down 1 semitone
[STD] Reset to original key
[+]  Transpose up 1 semitone
```

#### Scroll Settings (⚙️ icon)
- **AUTOSCROLL**: Toggle on/off
- **FART** (Speed): 1-100 slider
  - 1 = slow scroll
  - 100 = fast scroll

---

## 📝 Adding Songs

### Add a New Song
1. Create `Song_Title__Artist_Name.md` in `/library/`
2. Use this format:

```markdown
[Am]Verse lyrics here [C]with [G]chords
[Am]Second verse line
[C]Bridge section
[Dm]Final verse
```

### Chord Format
- Chords go in `[bracket]` notation: `[Am]`, `[C#m7b5]`, `[G]`
- Any note + suffix works: `[A]`, `[A#]`, `[Am]`, `[Am7]`, etc.

### Naming Convention
- Use underscores for spaces: `Song_Name__Artist.md`
- Result: "SONG NAME - ARTIST" in library
- Recommended: Include artist to avoid duplicates

---

## 🎨 Customization

### Colors (Black Stage Mode)
Edit [`components/ClientThemeProvider.tsx`](components/ClientThemeProvider.tsx):

```typescript
palette: {
  background: { default: '#000000' },  // Main background
  primary: { main: '#D187FF' },        // Chord color
  text: { primary: '#ffffff' },        // Text color
}
```

### Typography
Edit the `typography` section in same file to change:
- Font family (default: `Courier New`)
- Font sizes
- Line heights

### Layout Spacing
Edit CSS in:
- [`components/SongContent.module.css`](components/SongContent.module.css) - Song display
- [`components/Header.module.css`](components/Header.module.css) - Header sizing
- [`components/page.module.css`](components/page.module.css) - Library page

---

## 🔄 Transposition Algorithm

Located in [`lib/transposition.ts`](lib/transposition.ts):

```
Chromatic Scale: C, C#, D, D#, E, F, F#, G, G#, A, A#, B
Transpose: (index + steps) mod 12
```

Example: `[Am]` transposed +2 semitones = `[Bm]`

---

## 📱 Mobile Experience

### Responsive Breakpoints
| Aspect | Desktop | Mobile (<768px) |
|--------|---------|-----------------|
| Header | 80px | 70px |
| Logo | 125px | 100px |
| Font | 16px | 14px |
| Controls | Right-side | Stacked below |

### Touch Targets
- All buttons: **44×44px minimum** (WCAG AA compliance)
- Easy to tap on phones/tablets

---

## 🚀 Deployment Options

### Vercel (Recommended)
```bash
npm i -g vercel
vercel
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install && npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Traditional Node Host
```bash
npm run build
npm start
```

---

## 🔍 Troubleshooting

### Songs not showing?
- Check `/library/` folder exists
- Verify files end with `.md`
- Files must be UTF-8 encoded
- No special characters in filenames except `_` and `-`

### Logo not displaying?
- Ensure `public/logo.png` exists (already in project ✅)
- Try browser hard refresh: **Ctrl+Shift+R**
- Check browser console (F12) for errors

### Autoscroll stuttering?
- Close other browser tabs
- Reduce animation/effects on page
- Check CPU usage
- Slow? Try lower speed value (1-50)

### Transposition incorrect?
- Check chord format: `[Note]` is required
- Ensure note is A-G, optional #
- Examples: `[Am]` ✅, `[C#]` ✅, `[Dm7]` ✅

---

## 📊 File Structure Overview

```
playit-live/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Library page
│   ├── song/[slug]/       # Dynamic song routes
│   ├── api/songs/[slug]/  # Song API endpoint
│   └── globals.css        # Global styles
│
├── components/             # React components
│   ├── Header.tsx         # Fixed top bar
│   ├── SongContent.tsx    # Song display + controls
│   ├── LibraryClient.tsx  # Library view
│   └── ClientThemeProvider.tsx  # Material theme
│
├── lib/                    # Utilities
│   ├── transposition.ts   # Chord transposition logic
│   └── songs.ts           # Song file operations
│
├── library/                # Your song files (.md)
├── public/                 # Static files
│   └── logo.png           # App logo
│
├── package.json            # Dependencies
├── next.config.js         # Next.js config
└── tsconfig.json          # TypeScript config
```

---

## 📖 Key Features

✅ **Transposition** - Accurate chromatic scale calculation  
✅ **Autoscroll** - No iframe limitations, smooth scrolling  
✅ **Mobile-Optimized** - Responsive design, 44x44px touch targets  
✅ **Material Design 3** - Professional dark theme  
✅ **Fast HMR** - ~2s development hot reload  
✅ **TypeScript** - Type-safe development  
✅ **Production Build** - ~3MB total size  

---

## 🐛 Development Tips

### Debug Mode
```bash
# View Next.js version
next --version

# Check TypeScript
npx tsc --noEmit

# ESLint check
npm run lint
```

### Monitoring
```bash
# Check file sizes
du -sh app/ components/ lib/

# Monitor dependencies
npm ls --depth=0
```

---

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Material-UI (MUI) Guide](https://mui.com/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [CSS Modules](https://github.com/css-modules/css-modules)

---

## 🎓 Next Learning Steps

1. **Add localStorage** - Save favorites and transposition
2. **Keyboard shortcuts** - Arrow keys for navigation
3. **PWA support** - Offline access to songs
4. **Search feature** - Filter songs by title/artist
5. **Theme switcher** - Light/Dark/Custom themes

---

## 💬 Questions?

Check [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) for detailed technical information about the migration.

---

**Last Updated**: March 20, 2026  
**Version**: PlayIt! 2.0 (Next.js)  
**Status**: ✅ Production Ready
