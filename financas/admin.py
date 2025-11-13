from django.contrib import admin
from .models import *

admin.site.register(Usuario)
admin.site.register(conta)
admin.site.register(categoria)
admin.site.register(transacao)
admin.site.register(meta)

