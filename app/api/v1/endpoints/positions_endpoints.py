from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from app.api.v1.deps.auth_deps import get_current_user
from app.db.supabase_client import get_supabase_client

router = APIRouter(prefix="/positions", tags=["positions"])


@router.get("/")
async def get_positions(
    status_filter: Optional[str] = None,
    mode: str = "demo",
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase_client()
    
    res = supabase.table("trading_accounts").select("id").eq("user_id", current_user["id"]).eq("mode", mode).execute()
    if not res.data:
        return []
        
    account_id = res.data[0]["id"]
    
    table = "positions" if mode == "live" else "demo_trades"
    query = supabase.table(table).select("*").eq("trading_account_id", account_id)
    
    if status_filter:
        query = query.eq("status", status_filter)
        
    res = query.order("created_at", desc=True).limit(50).execute()
    return res.data if res.data else []


@router.post("/{position_id}/close")
async def close_position(
    position_id: str,
    mode: str = "demo",
    current_user: dict = Depends(get_current_user)
):
    # In a real app we would call position_service to market close on the broker
    # and update the DB. For now, just update DB status.
    supabase = get_supabase_client()
    
    res = supabase.table("trading_accounts").select("id").eq("user_id", current_user["id"]).eq("mode", mode).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")
        
    account_id = res.data[0]["id"]
    table = "positions" if mode == "live" else "demo_trades"
    
    update_res = supabase.table(table).update({"status": "closed", "close_reason": "manual_close"})\
        .eq("id", position_id).eq("trading_account_id", account_id).execute()
        
    if not update_res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Position not found.")
        
    return {"success": True, "position": update_res.data[0]}
