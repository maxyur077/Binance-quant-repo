from __future__ import annotations

from fastapi import APIRouter, Depends
from app.api.v1.deps.auth_deps import get_current_user
from app.db.supabase_client import get_supabase_client

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/performance")
async def get_user_performance(current_user: dict = Depends(get_current_user)):
    """
    Get aggregated performance analytics for the user's trades.
    """
    supabase = get_supabase_client()
    
    # In a production app, we would write a PostgreSQL RPC/View for this aggregation.
    # For now, we'll fetch demo trades and compute basic stats.
    
    # 1. Fetch account
    acc_res = supabase.table("trading_accounts").select("id").eq("user_id", current_user["id"]).eq("mode", "demo").execute()
    if not acc_res.data:
        return {"total_trades": 0, "win_rate": 0, "total_pnl": 0}
        
    account_id = acc_res.data[0]["id"]
    
    # 2. Fetch closed trades
    trades_res = supabase.table("demo_trades").select("pnl_usd").eq("trading_account_id", account_id).eq("status", "closed").execute()
    trades = trades_res.data if trades_res.data else []
    
    if not trades:
        return {"total_trades": 0, "win_rate": 0, "total_pnl": 0}
        
    total_trades = len(trades)
    wins = sum(1 for t in trades if float(t.get("pnl_usd") or 0) > 0)
    win_rate = (wins / total_trades) * 100
    total_pnl = sum(float(t.get("pnl_usd") or 0) for t in trades)
    
    return {
        "total_trades": total_trades,
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2)
    }
