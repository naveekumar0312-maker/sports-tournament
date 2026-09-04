from .models import Notification

def create_notification(recipient, title, message, notification_type=Notification.Type.TOURNAMENT_UPDATE, related_link=""):
    """Create a single notification for a specific user."""
    if recipient:
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            related_link=related_link
        )
    return None

def notify_team_members(team, title, message, notification_type=Notification.Type.TEAM_REGISTRATION, related_link=""):
    """Send notification to all player users in a given team."""
    notifications = []
    # Notify team creator
    if team.created_by:
        notifications.append(create_notification(team.created_by, title, message, notification_type, related_link))
    
    # Notify team members (players)
    for player in team.members.all():
        if player.user and player.user != team.created_by:
            notifications.append(create_notification(player.user, title, message, notification_type, related_link))
    return notifications

def notify_tournament_participants(tournament, title, message, notification_type=Notification.Type.TOURNAMENT_UPDATE, related_link=""):
    """Send notification to all registered teams and players in a tournament."""
    users_notified = set()
    notifications = []
    
    for reg in tournament.registrations.filter(status='APPROVED'):
        team = reg.team
        if team.created_by and team.created_by.id not in users_notified:
            users_notified.add(team.created_by.id)
            notifications.append(create_notification(team.created_by, title, message, notification_type, related_link))
        
        for player in team.members.all():
            if player.user and player.user.id not in users_notified:
                users_notified.add(player.user.id)
                notifications.append(create_notification(player.user, title, message, notification_type, related_link))
                
    return notifications
