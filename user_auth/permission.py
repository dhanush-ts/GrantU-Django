from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.Mentee == request.user or obj.Mentor == request.user
        return (obj.Mentee == request.user and obj.Selection_By=="mentor") or (obj.Mentor == request.user and obj.Selection_By=="mentee")