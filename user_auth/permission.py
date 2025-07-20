from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwner(BasePermission):
    
    def has_permission(self, request, view):
        return request.user is not None

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.Mentee == request.user or obj.Mentor == request.user
        return (obj.Mentee == request.user and obj.Selection_By=="mentor") or (obj.Mentor == request.user and obj.Selection_By=="mentee")

class BookingOwner(BasePermission):
    
    def has_permission(self, request, view):
        return request.user is not None

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.Booking.Mentee == request.user or obj.Booking.Mentor == request.user