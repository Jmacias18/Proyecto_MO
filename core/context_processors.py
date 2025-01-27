def user_groups(request):
    if request.user.is_authenticated:
        groups = request.user.groups.values_list('name', flat=True)
    else:
        groups = []
    return {'user_groups': groups}