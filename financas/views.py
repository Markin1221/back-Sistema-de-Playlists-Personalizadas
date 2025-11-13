from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from .models import *
from django.views import View
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal

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
#esta porra tem template

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
                return redirect('financas:dashboard')
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
#esta porra tem template

class dashBoardView(View):
    def get(self, request):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("login_cadastro")

        contas = conta.objects.filter(id_usuario=usuario)
        usuario_obj = Usuario.objects.get(id_usuario=usuario.id_usuario)
        metas = meta.objects.filter(id_usuario=usuario, concluida=False)
        transacoes = transacao.objects.filter(id_conta__id_usuario=usuario).order_by('-data_transacao')[:5]
        total_saldo = contas.aggregate(total=Sum('saldo_inicial'))['total'] or 0
        total_renda = (usuario.renda_mensal or Decimal(0)) + (usuario.renda_variavel or Decimal(0))
        categorias = categoria.objects.filter(id_usuario=usuario)

        contexto = {
            'usuario': usuario_obj,
            'contas': contas,
            'metas': metas,
            'ultimas_transacoes': transacoes,
            'total_saldo': total_saldo,
            'total_renda': total_renda,
            'categorias': categorias,
        }
        return render(request, 'financas/dashboard.html', contexto)
#esta porra tem template


class contaDetailView(View):
    def get(self, request, id_usuario, id_conta):
        usuario = get_usuario_logado(request)
        if not usuario or usuario.id_usuario != id_usuario:
            return redirect("login_cadastro")

        # Pega a conta
        conta_obj = get_object_or_404(conta, id_conta=id_conta, id_usuario=usuario)

        # Pega todas as transações da conta
        transacoes = transacao.objects.filter(id_conta=conta_obj)

        # Calcula saldo a partir das transações (não usa o saldo antigo)
        saldo_calculado = 0
        total_entradas = 0
        total_saidas = 0

        for t in transacoes:
            if t.tipo == 'entrada':
                saldo_calculado += t.valor
                total_entradas += t.valor
            else:  # saída
                saldo_calculado -= t.valor
                total_saidas += t.valor

        # Atualiza o saldo no banco apenas com base nas transações
        conta_obj.saldo_inicial = saldo_calculado
        conta_obj.save(update_fields=['saldo_inicial'])

        contexto = {
            'conta': conta_obj,
            'transacoes': transacoes.order_by('-data_transacao'),
            'usuario': usuario,
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo_final': saldo_calculado,
            'cor_saldo': 'red' if saldo_calculado < 0 else 'green',
        }

        return render(request, 'financas/conta_detail.html', contexto)


class criarContasview(View):
    def get(self, request, id_usuario):
        usuario = get_usuario_logado(request)
        if not usuario or usuario.id_usuario != int(id_usuario):
            return redirect("login_cadastro")
        return render(request, 'financas/criar_conta.html')

    def post(self, request, id_usuario):
        usuario = get_usuario_logado(request)
        if not usuario or usuario.id_usuario != int(id_usuario):
            return redirect("login_cadastro")

        nome_conta = request.POST.get('nome_conta')
        tipo = request.POST.get('tipo')
        saldo_inicial = request.POST.get('saldo_inicial')
        descricao = request.POST.get('descricao')
        e_Credito = request.POST.get('e_Credito') == 'on'
        limite_credito = request.POST.get('limite_credito') if e_Credito else 0.00

        conta.objects.create(
            id_usuario=usuario,  # referência correta para o usuário
            nome_conta=nome_conta,
            tipo=tipo,
            saldo_inicial=saldo_inicial,
            descriçao=descricao,
            e_Credito=e_Credito,
            limite_credito=limite_credito
        )
        return redirect('financas:dashboard')


class contasView(View):
    def get(self, request, id_usuario):
        usuario = get_usuario_logado(request)
        if not usuario or usuario.id_usuario != id_usuario:
            return redirect("login_cadastro")

        contas = conta.objects.filter(id_usuario=usuario)
        contexto = {
            'contas': contas,
            'usuario': usuario  # <<< Adicione isso
        }
        return render(request, 'financas/contas.html', contexto)


class NovaTransicaoview(View):
    def get(self, request, id_usuario, id_conta):
        usuario = get_usuario_logado(request)
        if not usuario or usuario.id_usuario != id_usuario:
            return redirect("login_cadastro")

        conta_obj = get_object_or_404(conta, id_conta=id_conta, id_usuario=usuario)
        categorias = categoria.objects.filter(id_usuario=usuario)

        contexto = {'conta': conta_obj, 'categorias': categorias, 'usuario': usuario}
        return render(request, 'financas/nova_transacao.html', contexto)

    def post(self, request, id_usuario, id_conta):
        usuario = get_usuario_logado(request)
        if not usuario or usuario.id_usuario != id_usuario:
            return redirect("login_cadastro")

        conta_obj = get_object_or_404(conta, id_conta=id_conta, id_usuario=usuario)
        categoria_obj = get_object_or_404(categoria, id_categoria=request.POST.get('id_categoria'), id_usuario=usuario)

        # Cria a nova transação
        transacao.objects.create(
            id_conta=conta_obj,
            id_categoria=categoria_obj,
            valor=float(request.POST.get('valor')),
            data_transacao=request.POST.get('data_transacao'),
            descricao=request.POST.get('descricao'),
            tipo=request.POST.get('tipo'),
            metodo_pagamento=request.POST.get('metodo_pagamento')
        )

        # --- Atualiza o saldo da conta com todas as transações existentes ---
        transacoes = transacao.objects.filter(id_conta=conta_obj)
        saldo_atual = 0
        for t in transacoes:
            if t.tipo == 'entrada':
                saldo_atual += t.valor
            else:  # saída
                saldo_atual -= t.valor

        # Salva o saldo no banco
        conta_obj.saldo_inicial = saldo_atual
        conta_obj.save(update_fields=['saldo_inicial'])

        return redirect(reverse('financas:conta_detail', args=[id_usuario, id_conta]))

#esta porra tem template

class gastosGeraisview(View):
    def get(self, request, id_usuario):
        usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
        transacoes = transacao.objects.filter(id_conta__id_usuario=usuario).order_by('-data_transacao')
        contas = conta.objects.filter(id_usuario=usuario)
        categorias = categoria.objects.all()

        return render(request, 'financas/gastos_gerais.html', {
            'usuario': usuario,
            'transacoes': transacoes,
            'contas': contas,
            'categorias': categorias,
        })
#esta porra tem template

class gastosCategoriaView(View):
    def get(self, request, id_usuario):
        usuario = get_usuario_logado(request)
        if not usuario or usuario.id_usuario != id_usuario:
            return redirect("financas:login_cadastro")

        # Busca todas as categorias do usuário
        categorias = categoria.objects.filter(id_usuario=usuario)

        # Se o usuário não tiver categorias ainda
        if not categorias.exists():
            contexto = {
                'usuario': usuario,
                'categorias': [],
            }
            return render(request, 'financas/gastos_categoria.html', contexto)

        # Monta os dados de cada categoria
        categorias_dados = []
        for cat in categorias:
            transacoes = transacao.objects.filter(id_categoria=cat)
            total_gastos = transacoes.filter(tipo='saida').aggregate(total=Sum('valor'))['total'] or 0
            total_entradas = transacoes.filter(tipo='entrada').aggregate(total=Sum('valor'))['total'] or 0

            categorias_dados.append({
                'nome': cat.nome_categoria,  # <-- usa o campo real do seu model
                'descricao': getattr(cat, 'descricao', ''),  # evita erro se o campo não existir
                'total_gastos': total_gastos,
                'total_entradas': total_entradas,
            })

        contexto = {
            'usuario': usuario,
            'categorias': categorias_dados,
        }
        return render(request, 'financas/gastos_categoria.html', contexto)
#esta porra tem template

class CriarCategoriaView(View):
    def get(self, request):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("financas:login_cadastro")
        return render(request, 'financas/criar_categoria.html')

    def post(self, request):
        usuario = get_usuario_logado(request)
        if not usuario:
            return redirect("financas:login_cadastro")

        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')

        if not nome:
            messages.error(request, "O nome da categoria é obrigatório.")
            return redirect('financas:criar_categoria')

        categoria.objects.create(
            id_usuario=usuario,
            nome=nome,
            descricao=descricao
        )

        messages.success(request, f"Categoria '{nome}' criada com sucesso!")
        return redirect('financas:gastos_gerais', id_usuario=usuario.id_usuario) 
#esta porra tem template    

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
        return redirect('financas:dashboard')


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
