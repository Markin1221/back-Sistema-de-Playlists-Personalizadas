from django.db import models
import datetime
from django.utils import timezone


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    senha_hash = models.CharField(max_length=256)
    data_criacao = models.DateTimeField(default=timezone.now)
    renda_mensal = models.DecimalField(max_digits=10, decimal_places=2)
    renda_variavel = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return self.nome
    
    
    
class conta(models.Model):
    id_conta = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nome_conta = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    descriçao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(default=timezone.now)
    e_Credito = models.BooleanField(default=False)
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.nome_conta
    

class categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nome_categoria = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)  
    descricao = models.TextField(blank=True, null=True)
    icone = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nome_categoria


class transacao(models.Model):
    id_transacao = models.AutoField(primary_key=True)
    id_conta = models.ForeignKey(conta, on_delete=models.CASCADE)
    id_categoria = models.ForeignKey(categoria, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_transacao = models.DateTimeField(default=timezone.now)
    descricao = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=50) 
    metodo_pagamento = models.CharField(max_length=50, blank=True, null=True)
    criado_em = models.DateTimeField(default=timezone.now, blank=True, null=True)
    
    def __str__(self):
        return f"{self.tipo} - {self.valor}"
    
class meta(models.Model):
    id_meta = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nome_meta = models.CharField(max_length=100)
    valor_objetivo = models.DecimalField(max_digits=10, decimal_places=2)
    valor_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    inicio_meta = models.DateField(default=timezone.now, blank=True, null=True)
    data_alvo = models.DateField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    concluida = models.BooleanField(default=False)

    def __str__(self):
        return self.nome_meta
    
    
class orcamento(models.Model):
    id_orcamento = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_categoria = models.ForeignKey(categoria, on_delete=models.CASCADE)
    valor_limite = models.DecimalField(max_digits=10, decimal_places=2)
    mes_referencia = models.IntegerField()
    ano_referencia = models.IntegerField(default=timezone.now, blank=True, null=True)
    gasto_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"Orçamento {self.id_orcamento} para {self.id_categoria.nome_categoria} no mes {self.mes_referencia}/{self.ano_referencia}"

class TransacaoRecorrente(models.Model):
    FREQUENCIAS = [
        ('diario', 'Diário'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
        ('anual', 'Anual'),
    ]

    id_recorrente = models.AutoField(primary_key=True)
    id_conta = models.ForeignKey('conta', on_delete=models.CASCADE)
    id_categoria = models.ForeignKey('categoria', on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    frequencia = models.CharField(
        max_length=10,
        choices=FREQUENCIAS,
        default='mensal'
    )
    proximoa_data = models.DateField()
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    