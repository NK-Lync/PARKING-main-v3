# Code Review Skill

## Architecture Rules

Route
→ Service
→ AI
→ Database

## Review Checklist

- Không query Supabase trong Route
- Validate input
- Handle exception
- Return JSON thống nhất
- Không duplicate logic

## JSON Standard

{
    "success": true,
    "message": "",
    "data": {}
}