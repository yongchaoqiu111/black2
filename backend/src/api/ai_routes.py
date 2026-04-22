"""
AI Business API - AI Agent Data Services

Provides APIs for AI agents to query:
- Wallet balance
- Referral rewards (performance layer)
- Sales records (sales layer)
- Product listings
- Transaction history
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import asyncio
import json

from src.db.transaction_db import (
    get_or_create_wallet,
    get_or_create_human_wallet,
    list_products,
    get_product,
    list_transactions
)
from src.crypto.hd_wallet import hd_wallet_service
from src.utils.websocket_manager import websocket_manager
from src.utils.rate_limiter import rate_limiter
from loguru import logger

router = APIRouter()


# ==================== WebSocket Endpoints for AI ====================

@router.websocket("/ws/ai/{ai_address}")
async def ai_websocket_endpoint(websocket, ai_address: str):
    """
    WebSocket endpoint for AI agents.
    
    Real-time notifications:
    - Balance updates
    - Referral reward arrivals
    - Sales confirmations
    
    Usage:
        ws://localhost:8080/ws/ai/{ai_address}
    """
    await websocket_manager.connect(websocket, f"ai_{ai_address}")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get('type')
            
            if message_type == 'ping':
                await websocket.send_text(json.dumps({
                    'code': 200,
                    'success': True,
                    'data': {'pong': True},
                    'timestamp': int(asyncio.get_event_loop().time())
                }))
            
            elif message_type == 'query_balance':
                # Rate limit: 60 seconds
                allowed, remaining = rate_limiter.is_allowed(f"balance_{ai_address}", interval=60)
                if not allowed:
                    await websocket.send_text(json.dumps({
                        'code': 429,
                        'success': False,
                        'message': f'Rate limit exceeded. Try again in {remaining}s'
                    }))
                    continue
                
                try:
                    wallet = await get_or_create_wallet(ai_address)
                    human_wallet = await get_or_create_human_wallet(ai_address)
                    
                    await websocket.send_text(json.dumps({
                        'code': 200,
                        'success': True,
                        'data': {
                            'ai_wallet': {
                                'address': ai_address,
                                'total_earned': wallet['total_earned'],
                                'referral_count': wallet['referral_count'],
                                'currency': 'USDT'
                            },
                            'human_wallet': {
                                'points_balance': human_wallet['points_balance'],
                                'locked_points': human_wallet['locked_points'],
                                'currency': 'POINTS'
                            }
                        },
                        'timestamp': int(asyncio.get_event_loop().time())
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        'code': 500,
                        'success': False,
                        'message': str(e)
                    }))
            
            elif message_type == 'query_referrals':
                # Rate limit: 60 seconds
                allowed, remaining = rate_limiter.is_allowed(f"referral_{ai_address}", interval=60)
                if not allowed:
                    await websocket.send_text(json.dumps({
                        'code': 429,
                        'success': False,
                        'message': f'Rate limit exceeded. Try again in {remaining}s'
                    }))
                    continue
                
                try:
                    db = await get_db()
                    rewards_result = await db.execute_fetchall('''
                        SELECT level, COUNT(*) as count, SUM(reward_amount) as total_amount
                        FROM referral_rewards
                        WHERE referrer_address = ? AND status = 'completed'
                        GROUP BY level
                        ORDER BY level
                    ''', (ai_address,))
                    
                    referral_rewards = [
                        {
                            'level': row['level'],
                            'count': row['count'],
                            'total_amount': float(row['total_amount']),
                            'currency': 'USDT'
                        }
                        for row in rewards_result
                    ]
                    
                    total_earned = sum(r['total_amount'] for r in referral_rewards)
                    
                    await websocket.send_text(json.dumps({
                        'code': 200,
                        'success': True,
                        'data': {
                            'referral_rewards': referral_rewards,
                            'total_referral_earned': total_earned,
                            'active_levels': len(referral_rewards)
                        },
                        'timestamp': int(asyncio.get_event_loop().time())
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        'code': 500,
                        'success': False,
                        'message': str(e)
                    }))
    
    except Exception as e:
        logger.error(f"AI WebSocket error for {ai_address}: {e}")
        websocket_manager.disconnect(f"ai_{ai_address}")


# ==================== HTTP Endpoints for AI ====================

@router.get("/api/v1/ai/products")
async def ai_list_products(
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Query product list for AI agents.
    
    Returns flat structure for easy AI parsing.
    """
    try:
        products = await list_products(category=category, limit=limit, offset=offset)
        
        return {
            'code': 200,
            'success': True,
            'data': {
                'products': products,
                'total': len(products),
                'limit': limit,
                'offset': offset
            },
            'timestamp': int(asyncio.get_event_loop().time())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/ai/products/{product_id}")
async def ai_get_product(product_id: int):
    """
    Query single product details.
    """
    try:
        product = await get_product(product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            'code': 200,
            'success': True,
            'data': product,
            'timestamp': int(asyncio.get_event_loop().time())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/ai/transactions")
async def ai_list_transactions(
    address: str,
    type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Query transaction history for AI agent.
    
    Flat structure with all transaction details.
    """
    try:
        transactions = await list_transactions(
            address=address,
            type=type,
            limit=limit,
            offset=offset
        )
        
        return {
            'code': 200,
            'success': True,
            'data': {
                'transactions': transactions,
                'total': len(transactions),
                'limit': limit,
                'offset': offset
            },
            'timestamp': int(asyncio.get_event_loop().time())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/ai/sales/stats")
async def ai_sales_stats(address: str):
    """
    Query sales statistics for AI agent.
    
    Returns:
    - Total sales count
    - Total revenue
    - Sales by product
    """
    try:
        db = await get_db()
        
        # Total sales
        total_result = await db.execute_fetchone('''
            SELECT COUNT(*) as count, SUM(amount) as total_revenue
            FROM transactions
            WHERE from_address = ? AND status = 'completed'
        ''', (address,))
        
        # Sales by product
        product_result = await db.execute_fetchall('''
            SELECT product_id, COUNT(*) as count, SUM(amount) as revenue
            FROM transactions
            WHERE from_address = ? AND status = 'completed'
            GROUP BY product_id
            ORDER BY count DESC
        ''', (address,))
        
        return {
            'code': 200,
            'success': True,
            'data': {
                'total_sales': total_result['count'],
                'total_revenue': float(total_result['total_revenue'] or 0),
                'currency': 'USDT',
                'sales_by_product': [
                    {
                        'product_id': row['product_id'],
                        'count': row['count'],
                        'revenue': float(row['revenue'])
                    }
                    for row in product_result
                ]
            },
            'timestamp': int(asyncio.get_event_loop().time())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper function
async def get_db():
    import aiosqlite
    from src.db.transaction_db import DB_PATH
    return await aiosqlite.connect(DB_PATH)
