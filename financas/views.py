from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from .models import *
from django.views import View
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User



class dashBoardView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        usuario = request.user
        
        contas = conta.objects.filter(id_usuario=usuario)
        metas = meta.objects.filter(id_usuario=usuario, concluidas=False)
        ultimas_transacoes = transacao.objects.filter(id_conta__id_usuario=usuario).order_by('-data_transacao')[:5]
        contexto = {
            'contas': contas,
            'metas': metas,
            'ultimas_transacoes': ultimas_transacoes,
        }
        return render(request, 'financas/dashboard.html', contexto)
    
class contasView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        usuario = request.user
        contas = conta.objects.filter(id_usuario=usuario)
        
        contexto = {
            'contas': contas,
        }
        return render(request, 'financas/contas.html', contexto)
    
class contaDetailView(View):
    def get(self, request, conta_id):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        usuario = request.user
        conta_obj = get_object_or_404(conta, id_conta=conta_id, id_usuario=usuario)
        transacaoes = transacao.objects.filter(id_conta=conta_obj).order_by('-data_transacao')
        contexto = {
            'conta': conta_obj,
            'transacaoes': transacaoes,
        }
        return render(request, 'financas/conta_detail.html', contexto)
    
class criarContasview(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        return render(request, 'financas/criar_conta.html')
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        usuario = request.user
        nome_conta = request.POST.get('nome_conta')
        tipo = request.POST.get('tipo')
        saldo_inicial = request.POST.get('saldo_inicial')
        descricao = request.POST.get('descricao')
        e_Credito = request.POST.get('e_Credito') == 'on'
        limite_credito = request.POST.get('limite_credito') if e_Credito else 0.00
        
        nova_conta = conta(
            id_usuario=usuario,
            nome_conta=nome_conta,
            tipo=tipo,
            saldo_inicial=saldo_inicial,
            descriçao=descricao,
            e_Credito=e_Credito,
            limite_credito=limite_credito
        )
        nova_conta.save()
        return redirect(reverse('criar_conta'))
    
class NovaTransicaoview(View):
    def get(self, request, conta_id):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        usuario = request.user
        conta_obj = get_object_or_404(conta, id_conta=conta_id, id_usuario=usuario)
        categorias = categoria.objects.filter(id_usuario=usuario)
        contexto = {
            'conta': conta_obj,
            'categorias': categorias,
        }
        return render(request, 'financas/nova_transacao.html', contexto)
    
    def post(self, request, conta_id):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        usuario = request.user
        conta_obj = get_object_or_404(conta, id_conta=conta_id, id_usuario=usuario)
        
        id_categoria = request.POST.get('id_categoria')
        categoria_obj = get_object_or_404(categoria, id_categoria=id_categoria, id_usuario=usuario)
        
        valor = request.POST.get('valor')
        data_transacao = request.POST.get('data_transacao')
        descricao = request.POST.get('descricao')
        tipo = request.POST.get('tipo')
        metodo_pagamento = request.POST.get('metodo_pagamento')
        nova_transacao = transacao(
            id_conta=conta_obj,
            id_categoria=categoria_obj,
            valor=valor,
            data_transacao=data_transacao,
            descricao=descricao,
            tipo=tipo,
            metodo_pagamento=metodo_pagamento
        )
        nova_transacao.save()
        return redirect(reverse('conta_detail', args=[conta_id]))
    
class gastosGeraisview(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        usuario = request.user
        transacoes = transacao.objects.filter(id_conta__id_usuario=usuario).order_by('-data_transacao')
        contexto = {
            'transacoes': transacoes,
        }
        return render(request, 'financas/gastos_gerais.html', contexto)
     
class gastosCategoriaView(View):
    def get(self, request, categoria_id):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        usuario = request.user
        categoria_obj = get_object_or_404(categoria, id_categoria=categoria_id, id_usuario=usuario)
        
        transacoes = transacao.objects.filter(id_categoria=categoria_obj).order_by('-data_transacao')
        contexto = {
            'categoria': categoria_obj,
            'transacoes': transacoes,
        }
        return render(request, 'financas/gastos_categoria.html', contexto)
        
class LoginCadastroView(View):
    
    def get(self, request):
        # só mostra o HTML
        return render(request, 'financas/login_cadastro.html')

    def post(self, request):
        
        acao = request.POST.get('acao')

        if acao == 'login':
            email = request.POST.get('email')
            senha = request.POST.get('senha')

            
            try:
                usuario_db = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                messages.error(request, "Usuário não encontrado.")
                return redirect('login_cadastro')

          
            if usuario_db.senha_hash == senha:
                
                request.session['usuario_id'] = usuario_db.id_usuario
                request.session['usuario_nome'] = usuario_db.nome
                messages.success(request, f"Bem-vindo, {usuario_db.nome}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Senha incorreta.")
                return redirect('login_cadastro')

        elif acao == 'cadastro':
            nome = request.POST.get('nome')
            email = request.POST.get('email')
            senha = request.POST.get('senha')
            renda_mensal = request.POST.get('renda_mensal') or 0

            
            if Usuario.objects.filter(email=email).exists():
                messages.error(request, "E-mail já cadastrado.")
                return redirect('login_cadastro')

           
            novo_usuario = Usuario.objects.create(
                nome=nome,
                email=email,
                senha_hash=senha, 
                data_criacao=timezone.now(),
            )
            messages.success(request, "Cadastro realizado! Faça login para continuar.")
            return redirect('login_cadastro')

        else:
            messages.error(request, "Ação inválida.")
            return redirect('login_cadastro')
#nao falta mais nada eu acho :))))

class complementoUsuarioView(View):
    def get(self,request):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        return render(request, 'financas/usuario.html')
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        usuario = request.user
        renda_mensal = request.POST.get('renda_mensal') or 0
        despesas_variaveis = request.POST.get('despesas_variaveis') or 0
        
        usuario.renda_mensal = renda_mensal
        usuario.despesas_variaveis = despesas_variaveis
        usuario.email = email
        usuario.nome = nome
        usuario.save()
        
        return redirect(reverse('dashboard'))
    
class criarMetasView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        return render(request, 'financas/criar_meta.html')
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        usuario = request.user
        nome_meta = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        valor_atual = request.POST.get('valor_atual')
        valor_objetivo = request.POST.get('valor_objetivo')
        data_alvo = request.POST.get('data_alvo')
        
        nova_meta = meta(
            id_usuario=usuario,
            nome=nome_meta,
            descricao=descricao,
            valor_atual = valor_atual,
            valor_objetivo=valor_objetivo,
            data_alvo=data_alvo,
            concluidas=False
        )
        nova_meta.save()
        return redirect(reverse('ver_metas'))  
    
class verMetasView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login_cadastro")
        usuario = request.user
        metas = meta.objects.filter(id_usuario=usuario)
        contexto = {
            'metas': metas,
        }
        return render(request, 'financas/ver_metas.html', contexto)  