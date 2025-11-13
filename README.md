# Knight Demo Game

Projeto demonstrativo de um jogo 2D desenvolvido com Pygame. O objetivo deste repositório é servir como trabalho para a disciplina e como base para experimentação com mecânicas de jogo (animações, IA simples, áudio dinâmico e interface).

Este projeto foi desenvolvido para a disciplina "Linguagem de Programação Aplicada" da UNINTER.
Curso: Análise e Desenvolvimento de Sistemas

## Descrição

O jogo é um protótipo de ação/platformer com foco em combate corpo-a-corpo. Possui menu principal, cena de gameplay com inimigos que perseguem e atacam o jogador, pickups de vida, efeitos visuais/sons, e uma camada de configurações.

## Principais features

- Tela de menu com navegação e seleção de opções (Iniciar, Configuração, Sair).
- Cena de gameplay com:
  - Jogador com movimento lateral, pulo, e ataques corpo-a-corpo (vários estados de ataque).
  - Sistema de animações por spritesheets (player e inimigos).
  - Inimigos com IA simples: detecção do jogador, perseguição e ataques com cooldown.
  - Hitboxes separadas da caixa visual e sistema de colisões para ataques.
  - Barra de HP e pickups de vida.
  - Efeitos visuais/sonoros: hitsparks, slow-motion e zoom em impactos.

- Menus e fluxos de UI: pause, configurações e tela de morte.

- Gerenciador de áudio (`AudioManager`) com suporte a SFX, variações por pasta e crossfade de músicas.

## Controles

- Mover: ← / A (esquerda), → / D (direita)
- Pular: Space / W / ↑
- Atacar: Ctrl esquerdo/direito
- Pausar / Voltar ao menu: Esc
- Navegar menus: ↑/W e ↓/S • Enter para selecionar

## Estrutura de ativos

- `src/assets/images/` — spritesheets do jogador e inimigos
- `src/assets/sounds/` — efeitos sonoros (sfx)
- `src/assets/music/` — trilhas de música (menu, gameplay)

Créditos dos assets
-------------------
Alguns assets utilizados foram obtidos de coleções gratuitas no itch.io e modificados para o projeto.

Fontes dos assets (atribuição):

- Fantasy Knight — personagem e sprites animados por aamatniekss (itch.io)
  - https://aamatniekss.itch.io/fantasy-knight-free-pixelart-animated-character
- PixelCombat — sprites e efeitos de combate por heltonyan (itch.io)
  - https://heltonyan.itch.io/pixelcombat

Observação: as imagens e sprites foram adaptadas (recorte/escala/cores) para melhor se adequarem ao jogo.

## Configurações e constantes relevantes

O arquivo `src/game/settings.py` contém constantes como `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `FPS`, cores, `HITBOX_WIDTH`, `HITBOX_HEIGHT` e outras constantes de gameplay.

## Como executar

Requisitos mínimos:

- Python 3.8+ (recomendado)
- Dependências listadas em `requirements.txt` (principalmente `pygame`).

Instalação:

```powershell
cd <pasta-do-repositorio>
python -m pip install -r requirements.txt
```

Execução:

```powershell
python .\src\main.py
```

## Licença

O projeto segue a licença MIT. Se desejar, adicione um arquivo `LICENSE` na raiz.