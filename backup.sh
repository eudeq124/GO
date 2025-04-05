#!/bin/bash

# Configuration
APP_NAME="goldeaf_bank"
BACKUP_DIR="/var/backups/$APP_NAME"
APP_DIR="/var/www/$APP_NAME"
RETENTION_DAYS=30
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_NAME="${APP_NAME}_${DATE}"

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Création du répertoire de sauvegarde
mkdir -p "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/daily"
mkdir -p "$BACKUP_DIR/weekly"
mkdir -p "$BACKUP_DIR/monthly"

# Fonction de log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

# Sauvegarde de la base de données
backup_database() {
    log "Sauvegarde de la base de données..."
    if [ -f "$APP_DIR/instance/database.db" ]; then
        sqlite3 "$APP_DIR/instance/database.db" ".backup '$BACKUP_DIR/daily/$BACKUP_NAME.db'"
        if [ $? -eq 0 ]; then
            log "Base de données sauvegardée avec succès"
        else
            error "Échec de la sauvegarde de la base de données"
            return 1
        fi
    else
        error "Base de données non trouvée"
        return 1
    fi
}

# Sauvegarde des fichiers de configuration
backup_config() {
    log "Sauvegarde des fichiers de configuration..."
    tar -czf "$BACKUP_DIR/daily/$BACKUP_NAME.config.tar.gz" \
        -C "$APP_DIR" \
        nginx.conf \
        .env \
        requirements.txt \
        2>/dev/null

    if [ $? -eq 0 ]; then
        log "Fichiers de configuration sauvegardés avec succès"
    else
        error "Échec de la sauvegarde des fichiers de configuration"
        return 1
    fi
}

# Sauvegarde des fichiers statiques
backup_static() {
    log "Sauvegarde des fichiers statiques..."
    tar -czf "$BACKUP_DIR/daily/$BACKUP_NAME.static.tar.gz" \
        -C "$APP_DIR" \
        static/ \
        2>/dev/null

    if [ $? -eq 0 ]; then
        log "Fichiers statiques sauvegardés avec succès"
    else
        error "Échec de la sauvegarde des fichiers statiques"
        return 1
    fi
}

# Rotation des sauvegardes
rotate_backups() {
    log "Rotation des sauvegardes..."
    
    # Copie hebdomadaire (chaque dimanche)
    if [ $(date +%u) -eq 7 ]; then
        cp "$BACKUP_DIR/daily/$BACKUP_NAME"* "$BACKUP_DIR/weekly/"
    fi
    
    # Copie mensuelle (premier jour du mois)
    if [ $(date +%d) -eq 01 ]; then
        cp "$BACKUP_DIR/daily/$BACKUP_NAME"* "$BACKUP_DIR/monthly/"
    fi
    
    # Suppression des anciennes sauvegardes
    find "$BACKUP_DIR/daily" -type f -mtime +7 -delete
    find "$BACKUP_DIR/weekly" -type f -mtime +30 -delete
    find "$BACKUP_DIR/monthly" -type f -mtime +365 -delete
    
    log "Rotation des sauvegardes terminée"
}

# Compression des sauvegardes du jour
compress_backups() {
    log "Compression des sauvegardes..."
    cd "$BACKUP_DIR/daily"
    tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"* --remove-files
    log "Compression terminée"
}

# Exécution des sauvegardes
main() {
    log "Début de la sauvegarde..."
    
    backup_database
    backup_config
    backup_static
    compress_backups
    rotate_backups
    
    log "Sauvegarde terminée avec succès"
}

main
