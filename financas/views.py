from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from .models import *
from django.views import View
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages


# 🧠 Função auxiliar para pegar o usuário logado
def get_usuario_logado(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return None
    try:
        return Usuario.objects.get(id_usuario=usuario_id)
    except Usuario.DoesNotExist:
        return None

class MainView(View):
    def get(self, request):
        return redirect("financas:login_cadastro")


class dashBoardView(View):
    def get(self, request):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("login_cadastro")

        contas = conta.objects.filter(id_usuario=usuario)
        metas = meta.objects.filter(id_usuario=usuario, concluida=False)
        ultimas_transacoes = transacao.objects.filter(id_conta__id_usuario=usuario).order_by('-data_transacao')[:5]

        contexto = {
            'contas': contas,
            'metas': metas,
            'ultimas_transacoes': ultimas_transacoes,
        }
        return render(request, 'financas/dashboard.html', contexto)


class contasView(View):
    def get(self, request):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("login_cadastro")

        contas = conta.objects.filter(id_usuario=usuario)
        return render(request, 'financas/contas.html', {'contas': contas})


class contaDetailView(View):
    def get(self, request, conta_id):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("login_cadastro")

        conta_obj = get_object_or_404(conta, id_conta=conta_id, id_usuario=usuario)
        transacoes = transacao.objects.filter(id_conta=conta_obj).order_by('-data_transacao')

        contexto = {
            'conta': conta_obj,
            'transacoes': transacoes,
        }
        return render(request, 'financas/conta_detail.html', contexto)


class criarContasview(View):
    def get(self, request):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("login_cadastro")
        return render(request, 'financas/criar_conta.html')

    def post(self, request):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("login_cadastro")

        nome_conta = request.POST.get('nome_conta')
        tipo = request.POST.get('tipo')
        saldo_inicial = request.POST.get('saldo_inicial')
        descricao = request.POST.get('descricao')
        e_Credito = request.POST.get('e_Credito') == 'on'
        limite_credito = request.POST.get('limite_credito') if e_Credito else 0.00

        conta.objects.create(
            id_usuario=usuario,
            nome_conta=nome_conta,
            tipo=tipo,
            saldo_inicial=saldo_inicial,
            descriçao=descricao,
            e_Credito=e_Credito,
            limite_credito=limite_credito
        )
        return redirect('financas:dashboard')


class NovaTransicaoview(View):
    def get(self, request, conta_id):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("login_cadastro")

        conta_obj = get_object_or_404(conta, id_conta=conta_id, id_usuario=usuario)
        categorias = categoria.objects.filter(id_usuario=usuario)

        contexto = {'conta': conta_obj, 'categorias': categorias}
        return render(request, 'financas/nova_transacao.html', contexto)

    def post(self, request, conta_id):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("login_cadastro")

        conta_obj = get_object_or_404(conta, id_conta=conta_id, id_usuario=usuario)
        categoria_obj = get_object_or_404(categoria, id_categoria=request.POST.get('id_categoria'), id_usuario=usuario)

        transacao.objects.create(
            id_conta=conta_obj,
            id_categoria=categoria_obj,
            valor=request.POST.get('valor'),
            data_transacao=request.POST.get('data_transacao'),
            descricao=request.POST.get('descricao'),
            tipo=request.POST.get('tipo'),
            metodo_pagamento=request.POST.get('metodo_pagamento')
        )

        return redirect(reverse('financas:conta_detail', args=[conta_id]))


class gastosGeraisview(View):
    def get(self, request):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("login_cadastro")

        transacoes = transacao.objects.filter(id_conta__id_usuario=usuario).order_by('-data_transacao')
        return render(request, 'financas/gastos_gerais.html', {'transacoes': transacoes})


class gastosCategoriaView(View):
    def get(self, request, categoria_id):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("login_cadastro")

        categoria_obj = get_object_or_404(categoria, id_categoria=categoria_id, id_usuario=usuario)
        transacoes = transacao.objects.filter(id_categoria=categoria_obj).order_by('-data_transacao')

        return render(request, 'financas/gastos_categoria.html', {'categoria': categoria_obj, 'transacoes': transacoes})


class LoginCadastroView(View):
    def get(self, request):
        return render(request, 'financas/login_cadastro.html')

    def post(self, request):
        acao = request.POST.get('acao')

        # LOGIN
        if acao == 'login':
            email = request.POST.get('email')
            senha = request.POST.get('senha')

            try:
                usuario_db = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                messages.error(request, "Usuário não encontrado.")
                return redirect('financas:login_cadastro')

            if usuario_db.senha_hash == senha:
                request.session['usuario_id'] = usuario_db.id_usuario
                request.session['usuario_nome'] = usuario_db.nome
                messages.success(request, f"Bem-vindo, {usuario_db.nome}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Senha incorreta.")
                return redirect('financas:login_cadastro')

        # CADASTRO
        elif acao == 'cadastro':
            nome = request.POST.get('nome_cadastro')
            email = request.POST.get('email_cadastro')
            senha = request.POST.get('senha_cadastro')

            if Usuario.objects.filter(email=email).exists():
                messages.error(request, "E-mail já cadastrado.")
                return redirect('financas:login_cadastro')

            Usuario.objects.create(
                nome=nome,
                email=email,
                senha_hash=senha,
                data_criacao=timezone.now()
            )

            messages.success(request, "Cadastro realizado! Faça login para continuar.")
            return redirect('financas:login_cadastro')

        else:
            messages.error(request, "Ação inválida.")
            return redirect('financas:login_cadastro')


class complementoUsuarioView(View):
    def get(self, request):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("financas:login_cadastro")
        return render(request, 'financas/usuario.html', {'usuario': usuario})

    def post(self, request):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("financas:login_cadastro")

        usuario.nome = request.POST.get('nome')
        usuario.email = request.POST.get('email')
        usuario.renda_mensal = request.POST.get('renda_mensal') or 0
        usuario.renda_variavel = request.POST.get('despesas_variaveis') or 0
        usuario.save()

        messages.success(request, "Dados atualizados com sucesso!")
        return redirect('dashboard')


class criarMetasView(View):
    def get(self, request):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("financas:login_cadastro")
        return render(request, 'financas/criar_meta.html')

    def post(self, request):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("financas:login_cadastro")

        meta.objects.create(
            id_usuario=usuario,
            nome_meta=request.POST.get('titulo'),
            descricao=request.POST.get('descricao'),
            valor_atual=request.POST.get('valor_atual'),
            valor_objetivo=request.POST.get('valor_objetivo'),
            data_alvo=request.POST.get('data_alvo'),
            concluida=False
        )
        return redirect('ver_metas')


class verMetasView(View):
    def get(self, request):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("financas:login_cadastro")

        metas = meta.objects.filter(id_usuario=usuario)
        return render(request, 'financas/ver_metas.html', {'metas': metas})
