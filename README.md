# Especialista — Nova Gente

Loja modular de especialistas de IA para experiências de autoconhecimento pelo WhatsApp.

**Status:** início de desenvolvimento (MVP). Ainda não é um serviço pronto para clientes reais.

## Experiência planejada
- Catálogo com 13 especialistas e linguagem comercial própria.
- Primeiro especialista a **R$ 9,90/mês**; cada adicional a **R$ 4,99/mês**.
- Um único login e um WhatsApp vinculado ao número verificado do assinante.
- Compra de adicionais sem criar outra conta; acesso liberado apenas após confirmação de pagamento.
- Troca de especialistas no mesmo chat, preservando o isolamento por cliente e a memória autorizada.

## Arquitetura
- **Loja e painel:** interface web.
- **API:** identidade, carrinho, assinatura, códigos temporários e permissões.
- **JEV:** classificação/roteamento (não autoriza pagamento nem acesso).
- **DeepSeek:** modelo conversacional a integrar.
- **WAHA:** transporte de mensagens a integrar.
- **Composio:** integrações externas opcionais, nunca substituto obrigatório do login.
- **Banco:** PostgreSQL na produção; persistência de demonstração pode ser local.

## Regras obrigatórias
1. Isolamento por usuário, cliente, especialista e versão de conteúdo.
2. Nenhum especialista liberado sem pagamento confirmado por backend.
3. Códigos de ativação de uso único, expiração e vínculo com o número de origem verificado.
4. Nenhuma API key, token, senha real, dado pessoal ou conteúdo protegido de terceiros no Git.
5. Os plugins são referências internas de capacidades; não estão conectados diretamente a este repositório.
6. Conteúdo emocional é educativo/reflexivo, não diagnóstico ou atendimento clínico.
7. Infraestrutura real só após homologação de segurança, custo, cobrança e LGPD.

## Fases
F0 Inventário e revisão de conteúdo → F1 Fundação → F2 Módulos → F3 IA/JEV → F4 WhatsApp → F5 Cobranças → F6 Interface final → F7 Segurança → F8 Publicação.

**Atenção:** não disponibilizar a versão de desenvolvimento como serviço comercial antes das integrações e testes.
