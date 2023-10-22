from django.contrib import admin
from bee.models import *

# Register your models here.
admin.site.register(WatchList)
admin.site.register(ReadList)
admin.site.register(Reaction_anime)
admin.site.register(Comment_anime)
admin.site.register(Reaction_manga)
admin.site.register(Comment_manga)