from flask import Blueprint, request, jsonify
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
import db

bp = Blueprint('api', __name__)


# ─── HELPERS ────────────────────────────────────────────────────────────────

def error(msg, code=400):
    return jsonify({"success": False, "error": msg}), code


def ok(data=None, msg="ok"):
    payload = {"success": True, "message": msg}
    if data is not None:
        payload.update(data)
    return jsonify(payload), 200


# ─── USER ENDPOINTS ──────────────────────────────────────────────────────────

@bp.route('/user/<device_id>', methods=['GET'])
def get_user(device_id):
    """Fetch or auto-create a user by device ID."""
    if not device_id:
        return error("device_id is required")
    user = db.get_or_create_user(device_id)
    badges = db.get_user_badges(device_id)
    today_session = db.get_today_session(device_id)

    return ok({
        "user": user,
        "badges": badges,
        "today_session": today_session,
        "already_played_today": today_session is not None and today_session.get("completed") == 1
    })


# ─── SESSION ENDPOINTS ───────────────────────────────────────────────────────

@bp.route('/session/start', methods=['POST'])
def start_session():
    """Start a new session for today. One session per device per day."""
    data = request.get_json(force=True)
    device_id = data.get('device_id')
    mood = data.get('mood')

    if not device_id or not mood:
        return error("device_id and mood are required")

    # Ensure user exists
    db.get_or_create_user(device_id)

    # Check if already played today
    today = db.get_today_session(device_id)
    if today and today.get('completed') == 1:
        return jsonify({
            "success": False,
            "already_completed": True,
            "message": "You've already completed today's session. Come back tomorrow! 🌱"
        }), 200

    # Create or return today's session
    if not today:
        session_id = db.create_session(device_id, mood)
    else:
        session_id = today['id']

    return ok({"session_id": session_id, "mood": mood}, "Session started!")


@bp.route('/session/progress', methods=['POST'])
def update_progress():
    """Update how many stages the player has completed."""
    data = request.get_json(force=True)
    device_id = data.get('device_id')
    stages_completed = data.get('stages_completed', 0)
    completed = data.get('completed', False)

    if not device_id:
        return error("device_id is required")

    db.update_session_progress(device_id, stages_completed, completed)
    return ok({"stages_completed": stages_completed}, "Progress saved!")


# ─── STREAK ENDPOINTS ────────────────────────────────────────────────────────

@bp.route('/streak/<device_id>', methods=['GET'])
def get_streak(device_id):
    """Get the current streak for a device."""
    if not device_id:
        return error("device_id is required")
    user = db.get_or_create_user(device_id)
    return ok({
        "streak": user.get("streak", 0),
        "max_streak": user.get("max_streak", 0),
        "total_sessions": user.get("total_sessions", 0)
    })


@bp.route('/streak/update', methods=['POST'])
def update_streak():
    """Update streak when a session is completed."""
    data = request.get_json(force=True)
    device_id = data.get('device_id')
    if not device_id:
        return error("device_id is required")

    new_streak = db.update_streak(device_id)
    return ok({"streak": new_streak}, f"Streak updated to {new_streak}!")


# ─── BADGE ENDPOINTS ─────────────────────────────────────────────────────────

VALID_BADGES = {
    "calm_mind":    {"icon": "🌿", "name": "Calm Mind"},
    "brave_speaker":{"icon": "🗣️",  "name": "Brave Speaker"},
    "focus_master": {"icon": "🎯", "name": "Focus Master"},
    "growth_star":  {"icon": "✨", "name": "Growth Star"},
    "first_bloom":  {"icon": "🌸", "name": "First Bloom"},
    "streak_7":     {"icon": "🔥", "name": "7-Day Streak"},
    "streak_30":    {"icon": "💎", "name": "30-Day Streak"},
}


@bp.route('/badges/<device_id>', methods=['GET'])
def get_badges(device_id):
    """Get all badges earned by this device."""
    badges = db.get_user_badges(device_id)
    return ok({"badges": badges})


@bp.route('/badges/award', methods=['POST'])
def award_badge():
    """Award a badge to a device."""
    data = request.get_json(force=True)
    device_id = data.get('device_id')
    badge_key = data.get('badge_key')

    if not device_id or not badge_key:
        return error("device_id and badge_key are required")

    if badge_key not in VALID_BADGES:
        return error(f"Unknown badge: {badge_key}")

    badge = VALID_BADGES[badge_key]
    awarded = db.award_badge(device_id, badge['name'], badge['icon'])

    # Check streak badges
    user = db.get_or_create_user(device_id)
    streak = user.get('streak', 0)
    if streak >= 7:
        db.award_badge(device_id, "7-Day Streak", "🔥")
    if streak >= 30:
        db.award_badge(device_id, "30-Day Streak", "💎")

    return ok({
        "awarded": awarded,
        "badge": badge,
        "all_badges": db.get_user_badges(device_id)
    }, "Badge awarded!" if awarded else "Badge already earned.")


# ─── HEALTH CHECK ────────────────────────────────────────────────────────────

@bp.route('/health', methods=['GET'])
def health():
    return ok(msg="MindSprout API is running 🌱")