from typing import List, Optional
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import Goals
from app.schemas.goals import GoalCreate, GoalUpdate
from app.core.database import get_session


class GoalsService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_goals(self, user_id: int) -> List[Goals]:
        result = await self.db.execute(select(Goals).where(Goals.user_id == user_id))
        return result.scalars().all()

    async def get_goal(self, goal_id: int, user_id: int) -> Goals:
        goal = await self.db.get(Goals, goal_id)
        if not goal or goal.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found"
            )
        return goal

    async def create_goal(self, user_id: int, data: GoalCreate) -> Goals:
        goal = Goals(
            user_id=user_id,
            name=data.name,
            description=data.description,
            amount=data.amount,
            date_goals=data.date_goals,
        )
        self.db.add(goal)
        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def update_goal(self, goal_id: int, user_id: int, data: GoalUpdate) -> Goals:
        goal = await self.get_goal(goal_id, user_id)
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)
        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def delete_goal(self, goal_id: int, user_id: int) -> None:
        goal = await self.get_goal(goal_id, user_id)
        await self.db.delete(goal)
        await self.db.commit()


def get_goals_service(db_session: AsyncSession = Depends(get_session)) -> GoalsService:
    return GoalsService(db_session)
