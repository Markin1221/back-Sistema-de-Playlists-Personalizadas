from django.urls import path
from . import views

app_name = 'financas'

urlpatterns = [
    path('', views.MainView.as_view(), name='index'),
    
    path('dashboard/', views.dashBoardView.as_view(), name='dashboard'),
    
    path('login/', views.LoginCadastroView.as_view(), name='login_cadastro'),
    
    # Lista de contas do usuário
    path('contas/<int:id_usuario>/', views.contasView.as_view(), name='contas'),
    
    # Detalhe de uma conta específica
    path('conta/<int:id_usuario>/<int:id_conta>/', views.contaDetailView.as_view(), name='conta_detail'),
    
    # Criar nova conta (não precisa id_conta)
    path('criar_contas/<int:id_usuario>/', views.criarContasview.as_view(), name='criar_conta'),

    
    # Nova transação (precisa do usuário e da conta)
    path('nova_transacao/<int:id_usuario>/<int:id_conta>/', views.NovaTransicaoview.as_view(), name='nova_transacao'),
    
    # Gastos gerais e por categoria
    path('gastos_gerais/<int:id_usuario>/', views.gastosGeraisview.as_view(), name='gastos_gerais'),
    
    path('categoria/nova/', views.CriarCategoriaView.as_view(), name='criar_categoria'),
    
    path('gastos_categoria/<int:id_usuario>/', views.gastosCategoriaView.as_view(), name='gastos_categoria'),

    # Perfil e metas
    path('completar_perfil/<int:id_usuario>/', views.complementoUsuarioView.as_view(), name='completar_perfil'),
    
    path('criar_metas/<int:id_usuario>/', views.criarMetasView.as_view(), name='criar_metas'),
    
    path('ver_metas/<int:id_usuario>/', views.verMetasView.as_view(), name='ver_metas'),
]
