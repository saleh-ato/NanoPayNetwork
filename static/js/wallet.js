// FBA Coin Wallet JavaScript

class FBAWallet {
    constructor() {
        this.currentWallet = null;
        this.refreshInterval = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Wallet setup events
        document.getElementById('generate-wallet').addEventListener('click', () => this.generateWallet());
        document.getElementById('import-wallet').addEventListener('click', () => this.showImportForm());
        document.getElementById('confirm-import').addEventListener('click', () => this.importWallet());
        document.getElementById('cancel-import').addEventListener('click', () => this.hideImportForm());
        
        // Transaction events
        document.getElementById('send-form').addEventListener('submit', (e) => this.sendTransaction(e));
        document.getElementById('faucet-btn').addEventListener('click', () => this.requestFaucet());
        document.getElementById('refresh-history').addEventListener('click', () => this.refreshTransactionHistory());
    }

    async generateWallet() {
        try {
            this.showLoading('Generating wallet...');
            
            const response = await fetch('/api/wallet/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentWallet = result.data;
                this.showWalletDashboard();
                this.showToast('Wallet generated successfully!', 'success');
                this.startRefreshTimer();
            } else {
                this.showToast('Error generating wallet: ' + result.error, 'error');
            }
        } catch (error) {
            this.showToast('Error generating wallet: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    showImportForm() {
        document.getElementById('import-form').classList.remove('d-none');
    }

    hideImportForm() {
        document.getElementById('import-form').classList.add('d-none');
        document.getElementById('seed-input').value = '';
    }

    async importWallet() {
        try {
            const seed = document.getElementById('seed-input').value.trim();
            
            if (!seed) {
                this.showToast('Please enter a seed', 'error');
                return;
            }
            
            if (seed.length !== 64) {
                this.showToast('Seed must be 64 hex characters', 'error');
                return;
            }
            
            this.showLoading('Importing wallet...');
            
            const response = await fetch('/api/wallet/import', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ seed: seed })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentWallet = result.data;
                this.hideImportForm();
                this.showWalletDashboard();
                this.showToast('Wallet imported successfully!', 'success');
                this.startRefreshTimer();
            } else {
                this.showToast('Error importing wallet: ' + result.error, 'error');
            }
        } catch (error) {
            this.showToast('Error importing wallet: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    showWalletDashboard() {
        if (!this.currentWallet) return;
        
        // Hide setup section
        document.getElementById('wallet-setup').classList.add('d-none');
        
        // Show dashboard
        document.getElementById('wallet-dashboard').classList.remove('d-none');
        
        // Populate wallet info
        document.getElementById('wallet-address').value = this.currentWallet.address;
        
        // Refresh data
        this.refreshWalletData();
    }

    async refreshWalletData() {
        if (!this.currentWallet) return;
        
        try {
            // Get balance
            await this.refreshBalance();
            
            // Get transaction history
            await this.refreshTransactionHistory();
            
            // Get network stats
            await this.refreshNetworkStats();
            
        } catch (error) {
            console.error('Error refreshing wallet data:', error);
        }
    }

    async refreshBalance() {
        try {
            const response = await fetch(`/api/wallet/balance/${this.currentWallet.address}`);
            const result = await response.json();
            
            if (result.success) {
                document.getElementById('wallet-balance').textContent = result.data.balance.toFixed(2);
            }
        } catch (error) {
            console.error('Error refreshing balance:', error);
        }
    }

    async refreshTransactionHistory() {
        try {
            const response = await fetch(`/api/wallet/history/${this.currentWallet.address}?limit=10`);
            const result = await response.json();
            
            if (result.success) {
                this.updateTransactionTable(result.data.transactions);
            }
        } catch (error) {
            console.error('Error refreshing transaction history:', error);
        }
    }

    async refreshNetworkStats() {
        try {
            const response = await fetch('/api/ledger/stats');
            const result = await response.json();
            
            if (result.success) {
                const stats = result.data;
                document.getElementById('total-transactions').textContent = stats.total_transactions;
                document.getElementById('pending-transactions').textContent = stats.pending_transactions;
                document.getElementById('active-addresses').textContent = stats.active_addresses;
                document.getElementById('total-supply').textContent = stats.total_supply.toFixed(2);
            }
        } catch (error) {
            console.error('Error refreshing network stats:', error);
        }
    }

    updateTransactionTable(transactions) {
        const tbody = document.getElementById('transaction-history');
        
        if (transactions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No transactions yet</td></tr>';
            return;
        }
        
        tbody.innerHTML = transactions.map(tx => {
            const date = new Date(tx.timestamp * 1000).toLocaleString();
            const type = tx.type === 'sent' ? 'Sent' : 'Received';
            const typeClass = tx.type === 'sent' ? 'text-danger' : 'text-success';
            const address = tx.type === 'sent' ? tx.to_address : tx.from_address;
            const shortAddress = address.substring(0, 10) + '...';
            const amount = tx.type === 'sent' ? `-${tx.amount}` : `+${tx.amount}`;
            const amountClass = tx.type === 'sent' ? 'text-danger' : 'text-success';
            
            return `
                <tr>
                    <td>${date}</td>
                    <td class="${typeClass}">${type}</td>
                    <td><code>${shortAddress}</code></td>
                    <td class="${amountClass}">${amount} FBA</td>
                    <td><span class="badge bg-success">Confirmed</span></td>
                </tr>
            `;
        }).join('');
    }

    async sendTransaction(event) {
        event.preventDefault();
        
        if (!this.currentWallet) {
            this.showToast('No wallet loaded', 'error');
            return;
        }
        
        const recipientAddress = document.getElementById('recipient-address').value.trim();
        const amount = parseFloat(document.getElementById('send-amount').value);
        
        if (!recipientAddress || !amount) {
            this.showToast('Please fill in all fields', 'error');
            return;
        }
        
        if (amount <= 0) {
            this.showToast('Amount must be greater than 0', 'error');
            return;
        }
        
        try {
            this.showLoading('Sending transaction...');
            
            const response = await fetch('/api/wallet/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    from_address: this.currentWallet.address,
                    to_address: recipientAddress,
                    amount: amount,
                    private_key: this.currentWallet.private_key
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast(`Transaction sent successfully! Hash: ${result.data.transaction_hash.substring(0, 16)}...`, 'success');
                
                // Clear form
                document.getElementById('send-form').reset();
                
                // Refresh wallet data
                setTimeout(() => this.refreshWalletData(), 1000);
            } else {
                this.showToast('Error sending transaction: ' + result.error, 'error');
            }
        } catch (error) {
            this.showToast('Error sending transaction: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async requestFaucet() {
        if (!this.currentWallet) {
            this.showToast('No wallet loaded', 'error');
            return;
        }
        
        try {
            this.showLoading('Requesting faucet...');
            
            const response = await fetch('/api/ledger/faucet', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    address: this.currentWallet.address
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast(result.data.message, 'success');
                
                // Refresh wallet data
                setTimeout(() => this.refreshWalletData(), 1000);
            } else {
                this.showToast('Error requesting faucet: ' + result.error, 'error');
            }
        } catch (error) {
            this.showToast('Error requesting faucet: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    startRefreshTimer() {
        // Refresh every 10 seconds
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            this.refreshWalletData();
        }, 10000);
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastBody = document.getElementById('toast-body');
        
        // Set message
        toastBody.textContent = message;
        
        // Set background color based on type
        toast.className = 'toast';
        if (type === 'success') {
            toast.classList.add('bg-success', 'text-white');
        } else if (type === 'error') {
            toast.classList.add('bg-danger', 'text-white');
        } else {
            toast.classList.add('bg-info', 'text-white');
        }
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    showLoading(message) {
        // Simple loading implementation
        this.showToast(message, 'info');
    }

    hideLoading() {
        // Loading handled by toast auto-hide
    }
}

// Utility functions
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    element.setSelectionRange(0, 99999);
    document.execCommand('copy');
    
    // Show feedback
    wallet.showToast('Copied to clipboard!', 'success');
}

// Initialize wallet when page loads
const wallet = new FBAWallet();

// Load consensus visualization
document.addEventListener('DOMContentLoaded', () => {
    if (typeof window.FBAConsensus !== 'undefined') {
        window.consensus = new FBAConsensus();
        window.consensus.initialize();
    }
});
