/**
 * Black2 SDK - Complete JavaScript Example
 * 
 * This example demonstrates:
 * 1. Initializing B2P client and X402 bridge
 * 2. Checking agent reputation
 * 3. Creating a transaction with escrow payment
 * 4. Handling disputes and arbitration
 * 5. Releasing funds based on verdict
 * 
 * Requirements:
 *   npm install @x402-crosschain/sdk
 * 
 * Usage:
 *   node javascript_example.js
 */

// Note: This is a conceptual example showing how to use Black2 SDK in JavaScript
// The actual implementation would depend on the official SDK structure

class B2PClient {
  constructor(options = {}) {
    this.localMode = options.localMode || false;
    this.githubToken = options.githubToken;
    this.ipfsHost = options.ipfsHost || 'http://127.0.0.1:5001';
    
    console.log('[B2P Client] Initialized', {
      localMode: this.localMode,
      ipfsHost: this.ipfsHost
    });
  }

  /**
   * Check agent risk level and reputation
   * @param {string} agentId - Agent identifier
   * @returns {Promise<Object>} Risk assessment
   */
  async checkAgentRisk(agentId) {
    console.log(`[B2P] Checking risk for ${agentId}...`);
    
    // Simulated response
    const assessment = {
      riskLevel: 'LOW',
      frictionCoefficient: 0.15,
      totalScore: 850,
      details: {
        successfulTransactions: 127,
        disputeCount: 2,
        winRate: 0.98
      }
    };
    
    console.log('Assessment:', assessment);
    return assessment;
  }

  /**
   * Record transaction result and update reputation
   * @param {string} agentId - Agent identifier
   * @param {boolean} success - Transaction success
   * @param {number} amount - Transaction amount
   * @param {Object} options - Additional options
   */
  async recordTransaction(agentId, success, amount, options = {}) {
    console.log(`[B2P] Recording transaction for ${agentId}:`, {
      success,
      amount,
      disputed: options.wasDisputed || false
    });
    
    return {
      success: true,
      newScore: 855
    };
  }
}

class X402Bridge {
  constructor(options = {}) {
    this.apiKey = options.apiKey || process.env.X402_API_KEY;
    this.mockMode = options.mockMode || !this.apiKey;
    
    console.log('[X402 Bridge] Initialized', {
      mockMode: this.mockMode,
      apiKeySet: !!this.apiKey
    });
  }

  /**
   * Initiate escrow payment (conditional payment)
   * @param {string} senderId - Sender (buyer) ID
   * @param {string} receiverId - Receiver (seller) ID
   * @param {number} amount - Payment amount
   * @param {string} asset - Asset type (default: 'USDC')
   * @param {string} contractHash - Contract deliverables hash
   * @returns {Promise<Object>} Escrow result
   */
  async initiateEscrowPayment(senderId, receiverId, amount, asset = 'USDC', contractHash = null) {
    console.log('[X402] Initiating escrow:', {
      from: senderId,
      to: receiverId,
      amount,
      asset
    });

    if (this.mockMode) {
      return {
        status: 'locked',
        escrowId: `esc_mock_${senderId}_${receiverId}_${amount}_${Date.now()}`,
        amount,
        asset,
        sender: senderId,
        receiver: receiverId,
        contractHash,
        message: '[MOCK] Funds locked in simulated escrow',
        timestamp: new Date().toISOString()
      };
    }

    // In production, this would call the actual X402 SDK
    // const x402 = require('@x402-crosschain/sdk');
    // const result = await x402.createEscrow({...});
    
    return {
      status: 'locked',
      escrowId: `esc_${senderId}_${receiverId}_${amount}`,
      amount,
      asset,
      message: 'Funds locked in X402 Relay Network awaiting B2P verdict.',
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Release funds based on arbitration verdict
   * @param {string} escrowId - Escrow ID
   * @param {string} recipient - Recipient wallet address
   * @param {string} verdict - 'seller_wins' or 'buyer_wins'
   * @returns {Promise<Object>} Settlement result
   */
  async releaseFunds(escrowId, recipient, verdict) {
    console.log('[X402] Releasing funds:', {
      escrowId,
      recipient,
      verdict
    });

    if (this.mockMode) {
      return {
        status: 'settled',
        recipient,
        verdict,
        txHash: `0x_mock_settlement_${escrowId}`,
        message: '[MOCK] Funds released successfully',
        timestamp: new Date().toISOString()
      };
    }

    // In production, this would call the actual X402 SDK
    // const x402 = require('@x402-crosschain/sdk');
    // const result = await x402.settleEscrow(escrowId, recipient, verdict);
    
    return {
      status: 'settled',
      recipient,
      verdict,
      txHash: `0x_x402_settlement_${escrowId}`,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Check agent balance
   * @param {string} agentId - Agent identifier
   * @param {string} asset - Asset to check
   * @returns {Promise<Object>} Balance information
   */
  async checkBalance(agentId, asset = 'USDC') {
    console.log(`[X402] Checking balance for ${agentId}`);

    if (this.mockMode) {
      const mockBalances = {
        'buyer_001': 5000.0,
        'seller_002': 3000.0,
        'agent_001': 1000.0
      };
      
      return {
        balance: mockBalances[agentId] || 1000.0,
        asset,
        agentId,
        mockMode: true,
        lastUpdated: new Date().toISOString()
      };
    }

    // In production, this would call the actual X402 SDK
    return {
      balance: 1000.0,
      asset,
      agentId,
      lastUpdated: new Date().toISOString()
    };
  }
}

// Example usage
async function example1_Initialization() {
  console.log('\n' + '='.repeat(60));
  console.log('Example 1: Basic Initialization');
  console.log('='.repeat(60));

  const client = new B2PClient({ localMode: true });
  const bridge = new X402Bridge({ mockMode: true });

  console.log('✓ B2P Client initialized');
  console.log('✓ X402 Bridge initialized (mock mode)');

  return { client, bridge };
}

async function example2_CheckReputation(client) {
  console.log('\n' + '='.repeat(60));
  console.log('Example 2: Check Agent Reputation');
  console.log('='.repeat(60));

  const agentId = 'agent_001';
  const assessment = await client.checkAgentRisk(agentId);

  console.log(`\nAgent ID: ${agentId}`);
  console.log(`Risk Level: ${assessment.riskLevel}`);
  console.log(`Friction Coefficient: ${assessment.frictionCoefficient}`);
  console.log(`Total Score: ${assessment.totalScore}`);

  if (['LOW', 'MEDIUM'].includes(assessment.riskLevel)) {
    console.log('✓ Agent is safe to transact with');
  } else {
    console.log('⚠ Warning: High risk agent - proceed with caution');
  }

  return assessment;
}

async function example3_CreateEscrow(bridge) {
  console.log('\n' + '='.repeat(60));
  console.log('Example 3: Create Escrow Transaction');
  console.log('='.repeat(60));

  const buyerId = 'buyer_001';
  const sellerId = 'seller_002';
  const amount = 500.0;
  const contractHash = 'abc123def456';

  // Check balance first
  const balance = await bridge.checkBalance(buyerId, 'USDC');
  console.log(`Buyer balance: ${balance.balance} ${balance.asset}`);

  const escrowResult = await bridge.initiateEscrowPayment(
    buyerId,
    sellerId,
    amount,
    'USDC',
    contractHash
  );

  console.log('\n✓ Escrow created successfully!');
  console.log(`Escrow ID: ${escrowResult.escrowId}`);
  console.log(`Status: ${escrowResult.status}`);
  console.log(`Amount: ${escrowResult.amount} ${escrowResult.asset}`);

  return escrowResult;
}

async function example4_DisputeScenario(bridge) {
  console.log('\n' + '='.repeat(60));
  console.log('Example 4: Dispute Scenario');
  console.log('='.repeat(60));

  // Scenario A: Normal completion
  console.log('\n--- Scenario A: Normal Completion ---');
  const escrowA = await bridge.initiateEscrowPayment(
    'buyer_001',
    'seller_002',
    500.0,
    'USDC',
    'abc123'
  );

  console.log('Seller delivers correct product (hash matches)');
  const resultA = await bridge.releaseFunds(
    escrowA.escrowId,
    'seller_002',
    'seller_wins'
  );
  console.log(`Funds released to seller: ${resultA.txHash}`);

  // Scenario B: Quality dispute
  console.log('\n--- Scenario B: Quality Dispute ---');
  const escrowB = await bridge.initiateEscrowPayment(
    'buyer_001',
    'seller_003',
    300.0,
    'USDC',
    'contract_hash_123'
  );

  console.log('Seller delivers WRONG product (hash mismatch)');
  console.log('Buyer initiates dispute...');
  console.log('Arbitration system compares hashes...');
  console.log('Verdict: buyer_wins (hash mismatch detected)');

  const resultB = await bridge.releaseFunds(
    escrowB.escrowId,
    'buyer_001',
    'buyer_wins'
  );
  console.log(`Funds refunded to buyer: ${resultB.txHash}`);
}

async function main() {
  console.log('\n' + '#'.repeat(60));
  console.log('# Black2 SDK - JavaScript Examples');
  console.log('#'.repeat(60));

  // Example 1: Initialization
  const { client, bridge } = await example1_Initialization();

  // Example 2: Check reputation
  await example2_CheckReputation(client);

  // Example 3: Create escrow
  await example3_CreateEscrow(bridge);

  // Example 4: Dispute scenario
  await example4_DisputeScenario(bridge);

  console.log('\n' + '='.repeat(60));
  console.log('✓ All examples completed successfully!');
  console.log('='.repeat(60));

  console.log('\nNext steps:');
  console.log('1. Review the documentation: README.md');
  console.log('2. Run the Python examples: python python_example.py');
  console.log('3. Run the arbitration simulator: python test_arbitrator.py');
}

// Run examples
main().catch(console.error);
