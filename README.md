# 🎮 TOURNOI UNO - SITE WEB

Site web complet pour ton tournoi UNO avec authentification Telegram et design gaming moderne.

## 🚀 INSTALLATION RAPIDE

### 1. Prérequis
- Python 3.8 ou plus
- Un compte Telegram
- 5 minutes de ton temps

### 2. Installation

```bash
# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration

Ouvre le fichier `config.py` et modifie :

```python
# Tes IDs sont déjà configurés ! ✅
ADMIN_IDS = [
    7171751813,  # Toi (Asbath/Synth78) 
    7298908350   # Faty
]

# À remplir :
TELEGRAM_BOT_TOKEN = "METS_TON_TOKEN_ICI"  # Token de @Synth_78bot
```

**Comment obtenir le token du bot :**
1. Va sur Telegram
2. Parle à @BotFather
3. Tape `/mybots`
4. Sélectionne @Synth_78bot
5. Clique sur "API Token"
6. Copie-colle le token

### 4. Lancement

```bash
python app.py
```

Le site sera accessible sur : **http://localhost:5000**

## 📱 PAGES DU SITE (100% COMPLÈTES !)

✅ **Accueil** (`/`) - Hero section + matchs en vedette + stats en temps réel
✅ **Connexion** (`/login`) - Auth Telegram OAuth sécurisée
✅ **Inscription** (`/inscription`) - Formulaire avec CGU obligatoires
✅ **Dashboard** (`/dashboard`) - Tableau de bord utilisateur avec stats animées
✅ **Matchs** (`/matchs`) - Liste complète avec filtres + animations 3D
✅ **Classement** (`/classement`) - Top joueurs avec podium 3D + confettis
✅ **Profil** (`/profil`) - Stats détaillées + achievements + timeline
✅ **Admin** (`/admin`) - Dashboard admin complet (toi + Faty)
✅ **Mentions légales** (`/mentions-legales`) - Complètes
✅ **CGU** (`/cgu`) - Conditions générales complètes
✅ **Confidentialité** (`/politique-confidentialite`) - RGPD-compliant

## 🎨 DESIGN

**Style :** Gaming moderne avec animations DE MALADE
**Fonts :** Orbitron (titres) + Exo 2 (texte) - Polices distinctives gaming
**Couleurs :**
- Primaire : Bleu électrique (#2563eb)
- Secondaire : Rouge (#dc2626)
- Accent : Jaune/Or (#fbbf24)
- Background : Noir/Gris très foncé

**Features visuelles ÉPIQUES :**
- ✨ Animations CSS fluides partout
- 🌊 Arrière-plan animé avec gradients qui flottent
- ⚡ Effets glow sur hover + pulse
- 📱 100% responsive (mobile/tablet/desktop)
- 🎭 Transitions smooth avec cubic-bezier
- 🎯 Filtres animés avec ripple effect
- 🏆 Podium 3D qui monte depuis le bas
- 🎉 CONFETTIS pour le champion
- 💫 Cards qui flottent et s'inclinent en 3D
- 🔥 Boutons avec explosion au clic
- 📊 Barres de progression animées
- ⚡ Cercles radiaux qui tournent
- 🎨 Timeline avec dots qui pulsent
- 🌟 Achievements qui pop en 3D
- 💎 Effets shimmer sur les badges
- ⚡ Scan effect sur matchs en direct

## 🔐 SÉCURITÉ

**Authentification :**
- Auth via Telegram OAuth (officiel)
- Utilise l'ID Telegram permanent (pas le @username)
- Même si un joueur change son @, ses stats restent

**Protection des profils :**
- Chaque utilisateur ne peut voir QUE son propre profil
- Les admins (toi + Faty) ont accès au dashboard admin

**Base de données :**
- SQLite (fichier `tournoi_uno.db` créé automatiquement)
- Toutes les données sont locales et sécurisées

## 📊 BASE DE DONNÉES

Le système crée automatiquement 5 tables :

1. **utilisateurs** - Infos de base (ID Telegram, pseudo, photo, etc.)
2. **stats_joueurs** - Statistiques (victoires, défaites, winrate, gains)
3. **participants** - Inscriptions aux éditions
4. **matchs** - Tous les matchs du tournoi
5. **editions** - Historique des éditions

## ⚙️ CONFIGURATION AVANCÉE

### Changer l'édition actuelle
Dans `config.py` :
```python
EDITION_ACTUELLE = 3  # Change le numéro
```

### Modifier les frais
```python
FRAIS_MIN = 15  # Minimum pour participer
GAIN_BASE = 250  # Ce que tu offres
COMMISSION = 50  # Ce que tu gardes
```

### Ajouter un admin
Dans `config.py`, ajoute l'ID dans la liste :
```python
ADMIN_IDS = [
    7171751813,  # Toi
    7298908350,  # Faty
    123456789    # Nouvel admin
]
```

## 🚀 DÉPLOIEMENT EN LIGNE (GRATUIT)

### Option 1 : Railway.app (RECOMMANDÉ)

1. Va sur https://railway.app
2. Sign up avec GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Sélectionne ton repo
5. Railway détecte automatiquement Python
6. Ajoute les variables d'environnement :
   - `TELEGRAM_BOT_TOKEN` = ton token
7. Deploy ! 🎉

**Coût :** Gratuit jusqu'à 500h/mois

### Option 2 : Render.com

1. Va sur https://render.com
2. "New Web Service"
3. Connect GitHub
4. Configure :
   - Build Command : `pip install -r requirements.txt`
   - Start Command : `python app.py`
5. Deploy !

**Coût :** Gratuit (s'endort après 15min d'inactivité)

## 🐛 DÉPANNAGE

### Le site ne démarre pas
```bash
# Vérifie que les dépendances sont installées
pip list

# Réinstalle si besoin
pip install -r requirements.txt --upgrade
```

### Erreur de base de données
```bash
# Supprime la BDD et relance (elle se recréera)
rm tournoi_uno.db
python app.py
```

### Le token Telegram ne marche pas
- Vérifie que tu as copié le COMPLET token (commence par un nombre, finit par des lettres)
- Vérifie qu'il n'y a pas d'espaces avant/après
- Le token ressemble à : `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### La connexion Telegram ne fonctionne pas
- Assure-toi que le bot existe (@Synth_78bot)
- Vérifie que `TELEGRAM_BOT_USERNAME` dans config.py est correct
- Le widget Telegram peut prendre 2-3 secondes à charger

## 📝 TODO (Pages à finaliser)

Tu dois encore créer les pages :
- [ ] CGU complet (Conditions Générales d'Utilisation)
- [ ] Politique de confidentialité détaillée
- [ ] Page Dashboard (stats utilisateur)
- [ ] Page Matchs complète
- [ ] Page Classement complète
- [ ] Page Profil détaillée
- [ ] Dashboard Admin

**Je peux les créer si tu veux !** Dis-moi juste.

## 💡 PROCHAINES ÉTAPES

1. ✅ **Lance le site en local** pour tester
2. ✅ **Teste la connexion Telegram**
3. ✅ **Vérifie que tout s'affiche bien**
4. 📱 **Crée le bot Telegram** (on le fera après)
5. 🌐 **Déploie en ligne** sur Railway
6. 🎮 **Lance l'édition 3 !**

## 🆘 BESOIN D'AIDE ?

Si tu galères sur quelque chose :
1. Regarde les messages d'erreur dans le terminal
2. Vérifie config.py
3. Dis-moi le problème exact et je t'aide !

## 🎯 CE QUI EST PRÊT

✅ Design complet responsive avec animations ÉPIQUES
✅ Système d'auth Telegram sécurisé
✅ Structure de base de données complète
✅ Page d'accueil avec animations et stats
✅ Page de connexion Telegram OAuth
✅ Page d'inscription avec CGU obligatoires
✅ Dashboard utilisateur avec stats animées
✅ Page Matchs avec filtres et animations 3D
✅ Page Classement avec podium 3D + confettis
✅ Page Profil avec timeline et achievements
✅ Dashboard Admin (toi + Faty)
✅ Pages légales complètes (CGU, confidentialité, mentions)
✅ Configuration avec vos IDs (toi + Faty)
✅ 11 pages HTML complètes et fonctionnelles

## 🚧 CE QUI MANQUE (pour plus tard)

- Système de paiement Telegram Stars intégré
- Bot Telegram avec OpenAI (on le fait après !)
- API endpoints pour l'admin (créer matchs, etc.)
- Export CSV des données
- Notifications push

---

**Créé pour Asbath (17 ans, Bénin) 🇧🇯**
**Bot : @Synth_78bot**
**Édition actuelle : 2**

Let's go champion ! 🚀🎮
