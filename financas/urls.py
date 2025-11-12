from django.urls import path
from . import views


app_name = 'financas'

urlpatterns = [
    path('', views.MainView.as_view(), name='index'),  
    
    path('dashBoard/', views.dashBoardView.as_view(), name='dashboard'),
    
    path('login/', views.LoginCadastroView.as_view(), name='login_cadastro'),
    
    path('contas/<int:id_usuario>', views.contasView.as_view(), name='contas'),
    
    path('conta/<int:id_usuario>/<int:id_conta>/', views.contaDetailView.as_view(), name='conta_detail'),
    
    path('criar_contas/<int:id_usuario>/<int:id_conta>/', views.criarContasview.as_view(), name='criar_conta'),
    
    path('nova_transacao/<int:id_usuario>/<int:id_conta>/', views.NovaTransicaoview.as_view(), name='nova_transacao'),
    
    path('gastos_gerais/<int:id_usuario>/', views.gastosGeraisview.as_view(), name='gastos_gerais'),
    
    path('gastos_categoria/<int:id_usuario>/<int:id_categoria>', views.gastosCategoriaView.as_view(), name='gastos_categoria'),
    
    path('completar_perfil/<int:id_usuario>/', views.complementoUsuarioView.as_view(), name='completar_perfil'),
    
    path('criar_metas/<int:id_usuario>/', views.criarMetasView.as_view(), name='criar_metas'),
    
    path('ver_metas/<int:id_usuario>/', views.verMetasView.as_view(), name='ver_metas'),
    
]
