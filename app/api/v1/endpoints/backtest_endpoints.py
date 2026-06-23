from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.api.v1.deps.auth_deps import get_current_user
from app.services.backtest_service import backtest_service
from app.db.supabase_client import get_supabase_client

router = APIRouter(prefix="/backtests", tags=["backtests"])


class BacktestRequest(BaseModel):
    symbols: List[str]
    start_date: str
    end_date: str
    config: Dict[str, Any]


@router.post("/run")
async def run_backtest(req: BacktestRequest, current_user: dict = Depends(get_current_user)):
    """
    Initiates a new asynchronous backtest.
    """
    res = await backtest_service.start_backtest(
        user_id=current_user["id"],
        config=req.config,
        symbols=req.symbols,
        start_date=req.start_date,
        end_date=req.end_date
    )
    
    if not res.get("success"):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=res.get("error"))
        
    return res


@router.get("/")
async def list_backtests(current_user: dict = Depends(get_current_user), limit: int = 20):
    """
    Lists historical backtests for the user.
    """
    supabase = get_supabase_client()
    res = supabase.table("backtests").select("id, status, start_date, end_date, created_at, completed_at, result_summary").eq("user_id", current_user["id"]).order("created_at", desc=True).limit(limit).execute()
    
    return res.data if res.data else []


@router.get("/{backtest_id}")
async def get_backtest_details(backtest_id: str, current_user: dict = Depends(get_current_user)):
    """
    Gets full details of a specific backtest.
    """
    supabase = get_supabase_client()
    res = supabase.table("backtests").select("*").eq("id", backtest_id).eq("user_id", current_user["id"]).execute()
    
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backtest not found")
        
    backtest = res.data[0]
    
    # Optionally fetch the trades
    trades_res = supabase.table("backtest_trades").select("*").eq("backtest_id", backtest_id).execute()
    backtest["trades"] = trades_res.data if trades_res.data else []
    
    return backtest
