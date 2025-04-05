document.addEventListener('DOMContentLoaded', function() {
    // Gestion de la barre de progression pour les transferts
    function handleTransferProgress(transferId) {
        const progressBar = document.querySelector(`#progress-${transferId}`);
        if (!progressBar) return;

        let progress = 0;
        const interval = setInterval(() => {
            progress += 1;
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);

            if (progress === 67) {
                clearInterval(interval);
                // Attendre le code admin
                showAdminCodeModal(transferId);
            }
        }, 50);
    }

    // Modal pour le code admin
    function showAdminCodeModal(transferId) {
        const modal = new bootstrap.Modal(document.getElementById('adminCodeModal'));
        modal.show();

        document.getElementById('adminCodeForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const code = document.getElementById('adminCode').value;
            
            // Envoyer le code à l'API
            fetch('/api/verify-admin-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    transferId: transferId,
                    code: code
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    modal.hide();
                    continueTransfer(transferId);
                } else {
                    alert('Code incorrect');
                }
            });
        });
    }

    // Continuer le transfert après validation du code admin
    function continueTransfer(transferId) {
        const progressBar = document.querySelector(`#progress-${transferId}`);
        if (!progressBar) return;

        let progress = 67;
        const interval = setInterval(() => {
            progress += 1;
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);

            if (progress === 98) {
                clearInterval(interval);
                setTimeout(() => {
                    progress = 100;
                    progressBar.style.width = '100%';
                    progressBar.setAttribute('aria-valuenow', 100);
                    showTransferComplete();
                }, 1000);
            }
        }, 50);
    }

    // Afficher le message de transfert complété
    function showTransferComplete() {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show';
        alert.innerHTML = `
            Transfert complété avec succès!
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.container').insertBefore(alert, document.querySelector('.container').firstChild);
    }

    // Gestionnaire d'événements pour les formulaires de transfert
    const transferForms = document.querySelectorAll('.transfer-form');
    transferForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const transferId = this.dataset.transferId;
            handleTransferProgress(transferId);
        });
    });

    // Animation des cartes au survol
    const cards = document.querySelectorAll('.feature-card, .team-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});
