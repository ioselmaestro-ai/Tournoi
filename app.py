from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import sqlite3
from datetime import datetime
import secrets
import hashlib
import hmac
from functools import wraps
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
CORS(app)

# ==================== BASE DE DONNÉES ====================

def init_db():
    """Initialise la base de données"""
    conn = sqlite3.connect(config.DATABASE)
    cursor = conn.cursor()
    
    # Table utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_user_id TEXT NOT NULL UNIQUE,
            telegram_username TEXT,
            pseudo_affichage TEXT NOT NULL,
            prenom TEXT,
            photo_url TEXT,
            date_inscription TEXT NOT NULL,
            derniere_connexion TEXT,
            accepte_cgu INTEGER DEFAULT 0,
            accepte_confidentialite INTEGER DEFAULT 0,
            est_banni INTEGER DEFAULT 0
        )
    ''')
    
    # Table statistiques joueurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats_joueurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL UNIQUE,
            victoires INTEGER DEFAULT 0,
            defaites INTEGER DEFAULT 0,
            matchs_nuls INTEGER DEFAULT 0,
            total_matchs INTEGER DEFAULT 0,
            winrate REAL DEFAULT 0.0,
            total_gains INTEGER DEFAULT 0,
            predictions_justes INTEGER DEFAULT 0,
            predictions_totales INTEGER DEFAULT 0,
            cote REAL DEFAULT 1.0,
            niveau TEXT DEFAULT 'Bronze',
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
        )
    ''')
    
    # Table participants (inscriptions aux éditions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            edition INTEGER NOT NULL,
            frais_payes INTEGER DEFAULT 0,
            statut_paiement TEXT DEFAULT 'en_attente',
            transaction_id TEXT,
            date_paiement TEXT,
            date_inscription TEXT NOT NULL,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id),
            UNIQUE(utilisateur_id, edition)
        )
    ''')
    
    # Table matchs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matchs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edition INTEGER NOT NULL,
            numero_match INTEGER NOT NULL,
            joueur1_id INTEGER NOT NULL,
            joueur2_id INTEGER NOT NULL,
            gagnant_id INTEGER,
            score_j1 INTEGER DEFAULT 0,
            score_j2 INTEGER DEFAULT 0,
            statut TEXT DEFAULT 'a_venir',
            date_debut TEXT,
            date_fin TEXT,
            round TEXT,
            FOREIGN KEY (joueur1_id) REFERENCES utilisateurs(id),
            FOREIGN KEY (joueur2_id) REFERENCES utilisateurs(id),
            FOREIGN KEY (gagnant_id) REFERENCES utilisateurs(id)
        )
    ''')
    
    # Table éditions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS editions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_edition INTEGER NOT NULL UNIQUE,
            date_debut TEXT NOT NULL,
            date_fin TEXT,
            statut TEXT DEFAULT 'en_cours',
            gagnant_id INTEGER,
            total_pot INTEGER DEFAULT 0,
            FOREIGN KEY (gagnant_id) REFERENCES utilisateurs(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Créer l'édition actuelle si elle n'existe pas
    conn = sqlite3.connect(config.DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM editions WHERE numero_edition = ?', (config.EDITION_ACTUELLE,))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO editions (numero_edition, date_debut, statut)
            VALUES (?, ?, 'en_cours')
        ''', (config.EDITION_ACTUELLE, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
    conn.close()

def get_db_connection():
    """Crée une connexion à la base de données"""
    conn = sqlite3.connect(config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== DÉCORATEURS ====================

def login_required(f):
    """Vérifie que l'utilisateur est connecté"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vous devez être connecté pour accéder à cette page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Vérifie que l'utilisateur est admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        user = conn.execute('SELECT telegram_user_id FROM utilisateurs WHERE id = ?', 
                          (session['user_id'],)).fetchone()
        conn.close()
        
        if not user or int(user['telegram_user_id']) not in config.ADMIN_IDS:
            flash('Accès refusé : droits admin requis', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES PRINCIPALES ====================

@app.route('/')
def index():
    """Page d'accueil"""
    conn = get_db_connection()
    
    # Stats globales
    nb_participants = conn.execute('''
        SELECT COUNT(*) as count FROM participants 
        WHERE edition = ? AND statut_paiement = "paye"
    ''', (config.EDITION_ACTUELLE,)).fetchone()['count']
    
    pot_total_row = conn.execute('''
        SELECT SUM(frais_payes) as total FROM participants 
        WHERE edition = ? AND statut_paiement = "paye"
    ''', (config.EDITION_ACTUELLE,)).fetchone()
    pot_total = pot_total_row['total'] if pot_total_row['total'] else 0
    
    matchs_en_cours = conn.execute('''
        SELECT COUNT(*) as count FROM matchs 
        WHERE edition = ? AND statut = "en_cours"
    ''', (config.EDITION_ACTUELLE,)).fetchone()['count']
    
    # Matchs en vedette
    matchs_vedette = conn.execute('''
        SELECT m.id, m.numero_match, m.statut, m.date_debut,
               u1.pseudo_affichage as j1_pseudo, u1.photo_url as j1_photo,
               u2.pseudo_affichage as j2_pseudo, u2.photo_url as j2_photo,
               COALESCE(s1.victoires, 0) as j1_victoires, 
               COALESCE(s1.winrate, 0) as j1_winrate,
               COALESCE(s2.victoires, 0) as j2_victoires, 
               COALESCE(s2.winrate, 0) as j2_winrate
        FROM matchs m
        JOIN utilisateurs u1 ON m.joueur1_id = u1.id
        JOIN utilisateurs u2 ON m.joueur2_id = u2.id
        LEFT JOIN stats_joueurs s1 ON u1.id = s1.utilisateur_id
        LEFT JOIN stats_joueurs s2 ON u2.id = s2.utilisateur_id
        WHERE m.edition = ? AND m.statut IN ('en_cours', 'a_venir')
        ORDER BY m.statut DESC, m.date_debut ASC
        LIMIT 4
    ''', (config.EDITION_ACTUELLE,)).fetchall()
    
    conn.close()
    
    stats = {
        'nb_participants': nb_participants,
        'pot_total': pot_total,
        'pot_gagnant': pot_total + config.GAIN_BASE - config.COMMISSION,
        'matchs_en_cours': matchs_en_cours
    }
    
    return render_template('index.html', 
                         edition=config.EDITION_ACTUELLE,
                         stats=stats,
                         matchs_vedette=matchs_vedette,
                         logged_in='user_id' in session)

@app.route('/login')
def login():
    """Page de connexion"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html', bot_username=config.TELEGRAM_BOT_USERNAME)

@app.route('/inscription')
def inscription():
    """Page d'inscription"""
    return render_template('inscription.html')

@app.route('/api/telegram-auth', methods=['POST'])
def telegram_auth():
    """Authentification via Telegram"""
    data = request.get_json()
    
    telegram_user_id = str(data.get('id', ''))
    username = data.get('username', '')
    first_name = data.get('first_name', '')
    photo_url = data.get('photo_url', '')
    
    if not telegram_user_id:
        return jsonify({'success': False, 'message': 'Données invalides'}), 400
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM utilisateurs WHERE telegram_user_id = ?', 
                       (telegram_user_id,)).fetchone()
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if user:
        # Utilisateur existant - mise à jour
        conn.execute('''
            UPDATE utilisateurs 
            SET telegram_username = ?, derniere_connexion = ?, photo_url = ?
            WHERE telegram_user_id = ?
        ''', (username, now, photo_url, telegram_user_id))
        conn.commit()
        
        session['user_id'] = user['id']
        session['telegram_user_id'] = telegram_user_id
        session['pseudo'] = user['pseudo_affichage']
        session['is_admin'] = int(telegram_user_id) in config.ADMIN_IDS
        
        conn.close()
        return jsonify({'success': True, 'redirect': url_for('dashboard')})
    else:
        # Nouvel utilisateur
        conn.close()
        return jsonify({
            'success': True,
            'new_user': True,
            'telegram_data': {
                'id': telegram_user_id,
                'username': username,
                'first_name': first_name,
                'photo_url': photo_url
            }
        })

@app.route('/api/inscription', methods=['POST'])
def api_inscription():
    """Inscription d'un nouvel utilisateur"""
    data = request.get_json()
    
    telegram_user_id = str(data.get('telegram_user_id', ''))
    telegram_username = data.get('telegram_username', '')
    pseudo_affichage = data.get('pseudo_affichage', '').strip()
    prenom = data.get('prenom', '').strip()
    photo_url = data.get('photo_url', '')
    accepte_cgu = data.get('accepte_cgu', False)
    accepte_confidentialite = data.get('accepte_confidentialite', False)
    
    # Validations
    if not telegram_user_id or not pseudo_affichage:
        return jsonify({'success': False, 'message': 'Données manquantes'}), 400
    
    if not accepte_cgu or not accepte_confidentialite:
        return jsonify({'success': False, 'message': 'Vous devez accepter les CGU et la politique de confidentialité'}), 400
    
    if len(pseudo_affichage) < 3:
        return jsonify({'success': False, 'message': 'Le pseudo doit contenir au moins 3 caractères'}), 400
    
    conn = get_db_connection()
    
    # Vérifier si le pseudo est déjà pris
    existing = conn.execute('SELECT id FROM utilisateurs WHERE pseudo_affichage = ?', 
                           (pseudo_affichage,)).fetchone()
    if existing:
        conn.close()
        return jsonify({'success': False, 'message': 'Ce pseudo est déjà pris'}), 409
    
    # Créer l'utilisateur
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor = conn.execute('''
        INSERT INTO utilisateurs 
        (telegram_user_id, telegram_username, pseudo_affichage, prenom, photo_url,
         date_inscription, derniere_connexion, accepte_cgu, accepte_confidentialite)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1)
    ''', (telegram_user_id, telegram_username, pseudo_affichage, prenom, 
          photo_url, now, now))
    
    user_id = cursor.lastrowid
    
    # Créer les stats du joueur
    conn.execute('INSERT INTO stats_joueurs (utilisateur_id) VALUES (?)', (user_id,))
    
    conn.commit()
    conn.close()
    
    # Créer la session
    session['user_id'] = user_id
    session['telegram_user_id'] = telegram_user_id
    session['pseudo'] = pseudo_affichage
    session['is_admin'] = int(telegram_user_id) in config.ADMIN_IDS
    
    return jsonify({'success': True, 'redirect': url_for('dashboard')})

@app.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord utilisateur"""
    conn = get_db_connection()
    
    # Infos utilisateur
    user = conn.execute('''
        SELECT u.*, s.victoires, s.defaites, s.total_matchs, s.winrate, 
               s.total_gains, s.predictions_justes, s.predictions_totales, s.niveau
        FROM utilisateurs u
        LEFT JOIN stats_joueurs s ON u.id = s.utilisateur_id
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    # Participation à l'édition actuelle
    participation = conn.execute('''
        SELECT * FROM participants
        WHERE utilisateur_id = ? AND edition = ?
    ''', (session['user_id'], config.EDITION_ACTUELLE)).fetchone()
    
    # Prochains matchs
    prochains_matchs = conn.execute('''
        SELECT m.*, 
               u1.pseudo_affichage as adversaire
        FROM matchs m
        JOIN utilisateurs u1 ON (
            CASE WHEN m.joueur1_id = ? THEN m.joueur2_id ELSE m.joueur1_id END = u1.id
        )
        WHERE (m.joueur1_id = ? OR m.joueur2_id = ?)
        AND m.statut IN ('a_venir', 'en_cours')
        ORDER BY m.date_debut ASC
        LIMIT 5
    ''', (session['user_id'], session['user_id'], session['user_id'])).fetchall()
    
    conn.close()
    
    return render_template('dashboard.html',
                         user=user,
                         participation=participation,
                         prochains_matchs=prochains_matchs,
                         edition=config.EDITION_ACTUELLE)

@app.route('/matchs')
def matchs():
    """Page des matchs"""
    conn = get_db_connection()
    
    matchs_list = conn.execute('''
        SELECT m.*,
               u1.pseudo_affichage as j1_pseudo, u1.photo_url as j1_photo,
               u2.pseudo_affichage as j2_pseudo, u2.photo_url as j2_photo,
               COALESCE(s1.victoires, 0) as j1_victoires, 
               COALESCE(s1.winrate, 0) as j1_winrate,
               COALESCE(s2.victoires, 0) as j2_victoires, 
               COALESCE(s2.winrate, 0) as j2_winrate
        FROM matchs m
        JOIN utilisateurs u1 ON m.joueur1_id = u1.id
        JOIN utilisateurs u2 ON m.joueur2_id = u2.id
        LEFT JOIN stats_joueurs s1 ON u1.id = s1.utilisateur_id
        LEFT JOIN stats_joueurs s2 ON u2.id = s2.utilisateur_id
        WHERE m.edition = ?
        ORDER BY 
            CASE m.statut 
                WHEN 'en_cours' THEN 1 
                WHEN 'a_venir' THEN 2 
                ELSE 3 
            END,
            m.date_debut ASC
    ''', (config.EDITION_ACTUELLE,)).fetchall()
    
    conn.close()
    
    return render_template('matchs.html',
                         matchs=matchs_list,
                         edition=config.EDITION_ACTUELLE,
                         logged_in='user_id' in session)

@app.route('/classement')
def classement():
    """Page du classement"""
    conn = get_db_connection()
    
    classement_list = conn.execute('''
        SELECT u.id, u.pseudo_affichage, u.telegram_username, u.photo_url,
               s.victoires, s.defaites, s.total_matchs, s.winrate,
               s.total_gains, s.niveau, s.cote
        FROM utilisateurs u
        JOIN stats_joueurs s ON u.id = s.utilisateur_id
        WHERE s.total_matchs > 0
        ORDER BY s.victoires DESC, s.winrate DESC
        LIMIT 50
    ''').fetchall()
    
    conn.close()
    
    return render_template('classement.html',
                         classement=classement_list,
                         logged_in='user_id' in session)

@app.route('/profil')
@login_required
def profil():
    """Page de profil de l'utilisateur connecté"""
    conn = get_db_connection()
    
    # Infos complètes
    user = conn.execute('''
        SELECT u.*, s.*
        FROM utilisateurs u
        LEFT JOIN stats_joueurs s ON u.id = s.utilisateur_id
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    # Historique des matchs
    historique = conn.execute('''
        SELECT m.id, m.date_fin, m.score_j1, m.score_j2,
               u_adv.pseudo_affichage as adversaire,
               CASE 
                   WHEN m.gagnant_id = ? THEN 'victoire'
                   WHEN m.gagnant_id IS NULL THEN 'nul'
                   ELSE 'defaite'
               END as resultat
        FROM matchs m
        JOIN utilisateurs u_adv ON (
            CASE 
                WHEN m.joueur1_id = ? THEN m.joueur2_id
                ELSE m.joueur1_id
            END = u_adv.id
        )
        WHERE (m.joueur1_id = ? OR m.joueur2_id = ?)
        AND m.statut = 'termine'
        ORDER BY m.date_fin DESC
        LIMIT 20
    ''', (session['user_id'], session['user_id'], session['user_id'], session['user_id'])).fetchall()
    
    conn.close()
    
    return render_template('profil.html',
                         user=user,
                         historique=historique)

@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('index'))

# ==================== PAGES LÉGALES ====================

@app.route('/mentions-legales')
def mentions_legales():
    return render_template('legal/mentions_legales.html')

@app.route('/cgu')
def cgu():
    return render_template('legal/cgu.html')

@app.route('/politique-confidentialite')
def politique_confidentialite():
    return render_template('legal/politique_confidentialite.html')

# ==================== ADMIN ====================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Tableau de bord admin"""
    conn = get_db_connection()
    
    # Stats
    stats = {
        'total_utilisateurs': conn.execute('SELECT COUNT(*) as c FROM utilisateurs').fetchone()['c'],
        'participants_edition': conn.execute('''
            SELECT COUNT(*) as c FROM participants 
            WHERE edition = ? AND statut_paiement = "paye"
        ''', (config.EDITION_ACTUELLE,)).fetchone()['c'],
        'pot_total': conn.execute('''
            SELECT COALESCE(SUM(frais_payes), 0) as t FROM participants 
            WHERE edition = ? AND statut_paiement = "paye"
        ''', (config.EDITION_ACTUELLE,)).fetchone()['t'],
        'matchs_total': conn.execute('''
            SELECT COUNT(*) as c FROM matchs WHERE edition = ?
        ''', (config.EDITION_ACTUELLE,)).fetchone()['c']
    }
    
    # Dernières inscriptions
    dernieres_inscriptions = conn.execute('''
        SELECT u.pseudo_affichage, u.telegram_username, p.date_inscription, p.statut_paiement
        FROM participants p
        JOIN utilisateurs u ON p.utilisateur_id = u.id
        WHERE p.edition = ?
        ORDER BY p.date_inscription DESC
        LIMIT 10
    ''', (config.EDITION_ACTUELLE,)).fetchall()
    
    conn.close()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         dernieres_inscriptions=dernieres_inscriptions,
                         edition=config.EDITION_ACTUELLE)

# ==================== LANCEMENT ====================

if __name__ == '__main__':
    init_db()
    print("=" * 70)
    print("🎮 TOURNOI UNO - Site Web")
    print("=" * 70)
    print(f"📱 Accès : http://localhost:5000")
    print(f"🔐 Admin : http://localhost:5000/admin")
    print(f"🎯 Édition actuelle : {config.EDITION_ACTUELLE}")
    print("=" * 70)
    app.run(debug=config.DEBUG, host='0.0.0.0', port=5000)
