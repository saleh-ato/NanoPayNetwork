// FBA Consensus Visualization

class FBAConsensus {
    constructor() {
        this.nodes = {};
        this.quorumSlices = {};
        this.consensusData = {};
    }

    async initialize() {
        try {
            await this.loadNodesInfo();
            this.renderNodesVisualization();
            this.startConsensusMonitoring();
        } catch (error) {
            console.error('Error initializing consensus:', error);
        }
    }

    async loadNodesInfo() {
        try {
            const response = await fetch('/api/ledger/nodes');
            const result = await response.json();
            
            if (result.success) {
                this.nodes = result.data.nodes;
                this.quorumSlices = result.data.quorum_slices;
            }
        } catch (error) {
            console.error('Error loading nodes info:', error);
        }
    }

    renderNodesVisualization() {
        const container = document.getElementById('nodes-container');
        
        if (!container || !this.nodes) return;
        
        container.innerHTML = Object.keys(this.nodes).map(nodeId => {
            const node = this.nodes[nodeId];
            const trustedNodes = this.quorumSlices[nodeId] || [];
            
            return `
                <div class="col-md-4 col-lg-3 mb-3">
                    <div class="card node-card" data-node-id="${nodeId}">
                        <div class="card-body text-center">
                            <div class="node-status mb-2">
                                <i class="fas fa-circle text-success node-indicator" id="indicator-${nodeId}"></i>
                            </div>
                            <h6 class="card-title">${node.name}</h6>
                            <div class="small text-muted mb-2">
                                Stake: ${node.stake}
                            </div>
                            <div class="small text-muted">
                                Trusts: ${trustedNodes.length} nodes
                            </div>
                            <div class="consensus-info mt-2" id="consensus-${nodeId}">
                                <small class="text-success">
                                    <i class="fas fa-check-circle me-1"></i>
                                    Ready
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Add click handlers for node details
        container.querySelectorAll('.node-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const nodeId = e.currentTarget.dataset.nodeId;
                this.showNodeDetails(nodeId);
            });
        });
    }

    showNodeDetails(nodeId) {
        const node = this.nodes[nodeId];
        const trustedNodes = this.quorumSlices[nodeId] || [];
        
        if (!node) return;
        
        const trustedNodesText = trustedNodes.map(id => this.nodes[id]?.name || id).join(', ');
        
        const modal = `
            <div class="modal fade" id="nodeModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${node.name} Details</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-sm-4"><strong>Node ID:</strong></div>
                                <div class="col-sm-8"><code>${nodeId}</code></div>
                            </div>
                            <div class="row mt-2">
                                <div class="col-sm-4"><strong>Stake:</strong></div>
                                <div class="col-sm-8">${node.stake}</div>
                            </div>
                            <div class="row mt-2">
                                <div class="col-sm-4"><strong>Status:</strong></div>
                                <div class="col-sm-8">
                                    <span class="badge bg-success">Online</span>
                                </div>
                            </div>
                            <div class="row mt-2">
                                <div class="col-sm-4"><strong>Quorum Slice:</strong></div>
                                <div class="col-sm-8">${trustedNodesText || 'None'}</div>
                            </div>
                            <div class="row mt-2">
                                <div class="col-sm-4"><strong>Consensus Type:</strong></div>
                                <div class="col-sm-8">Federated Byzantine Agreement</div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal
        const existingModal = document.getElementById('nodeModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modal);
        
        // Show modal
        const bsModal = new bootstrap.Modal(document.getElementById('nodeModal'));
        bsModal.show();
        
        // Clean up modal after hide
        document.getElementById('nodeModal').addEventListener('hidden.bs.modal', function () {
            this.remove();
        });
    }

    async startConsensusMonitoring() {
        // Monitor pending transactions for consensus updates
        setInterval(async () => {
            await this.updateConsensusStatus();
        }, 5000);
    }

    async updateConsensusStatus() {
        try {
            // Get pending transactions
            const response = await fetch('/api/ledger/pending');
            const result = await response.json();
            
            if (result.success && result.data.transactions.length > 0) {
                // Show consensus activity
                this.showConsensusActivity(result.data.transactions);
            } else {
                // Reset to ready state
                this.resetConsensusIndicators();
            }
        } catch (error) {
            console.error('Error updating consensus status:', error);
        }
    }

    showConsensusActivity(pendingTransactions) {
        // Simulate consensus activity
        Object.keys(this.nodes).forEach(nodeId => {
            const indicator = document.getElementById(`indicator-${nodeId}`);
            const consensusInfo = document.getElementById(`consensus-${nodeId}`);
            
            if (indicator && consensusInfo) {
                // Show voting activity
                indicator.className = 'fas fa-circle text-warning node-indicator';
                consensusInfo.innerHTML = `
                    <small class="text-warning">
                        <i class="fas fa-vote-yea me-1"></i>
                        Voting...
                    </small>
                `;
                
                // Simulate completion after random delay
                setTimeout(() => {
                    indicator.className = 'fas fa-circle text-success node-indicator';
                    consensusInfo.innerHTML = `
                        <small class="text-success">
                            <i class="fas fa-check-circle me-1"></i>
                            Ready
                        </small>
                    `;
                }, Math.random() * 3000 + 1000);
            }
        });
    }

    resetConsensusIndicators() {
        Object.keys(this.nodes).forEach(nodeId => {
            const indicator = document.getElementById(`indicator-${nodeId}`);
            const consensusInfo = document.getElementById(`consensus-${nodeId}`);
            
            if (indicator && consensusInfo) {
                indicator.className = 'fas fa-circle text-success node-indicator';
                consensusInfo.innerHTML = `
                    <small class="text-success">
                        <i class="fas fa-check-circle me-1"></i>
                        Ready
                    </small>
                `;
            }
        });
    }

    simulateConsensusRound(transactionHash) {
        // Simulate a consensus round for educational purposes
        const steps = [
            'Preparing vote...',
            'Broadcasting vote...',
            'Collecting votes...',
            'Checking quorum...',
            'Consensus reached!'
        ];
        
        let stepIndex = 0;
        const interval = setInterval(() => {
            if (stepIndex < steps.length) {
                this.updateAllNodesStatus(steps[stepIndex]);
                stepIndex++;
            } else {
                clearInterval(interval);
                this.resetConsensusIndicators();
            }
        }, 1000);
    }

    updateAllNodesStatus(status) {
        Object.keys(this.nodes).forEach(nodeId => {
            const consensusInfo = document.getElementById(`consensus-${nodeId}`);
            if (consensusInfo) {
                consensusInfo.innerHTML = `
                    <small class="text-info">
                        <i class="fas fa-sync fa-spin me-1"></i>
                        ${status}
                    </small>
                `;
            }
        });
    }
}

// Make it globally available
window.FBAConsensus = FBAConsensus;
