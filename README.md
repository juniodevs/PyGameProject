# Knight Demo Game

Projeto demonstrativo de um jogo 2D desenvolvido com Pygame. O objetivo deste repositório é servir como trabalho para a disciplina e como base para experimentação com mecânicas de jogo (animações, IA simples, áudio dinâmico e interface).

Este projeto foi desenvolvido para a disciplina "Linguagem de Programação Aplicada" da UNINTER.
Curso: Análise e Desenvolvimento de Sistemas


## Descrição

O jogo é um protótipo de ação/platformer com foco em combate corpo-a-corpo. Possui menu principal, cena de gameplay com inimigos que perseguem e atacam o jogador, pickups de vida, efeitos visuais/sons, e uma camada de configurações.


## Principais features

- Tela de menu com navegação e seleção de opções (Iniciar, Configuração, Sair).
- Cena de gameplay com:
  - Jogador com movimento lateral, pulo, e ataques corpo-a-corpo (alternância entre dois ataques para variedade).
  - Sistema de animações por spritesheets (player e inimigos), com estados: idle, run, turn, attack1, attack2, jump, fall, hit, death.
  - Inimigos com IA simples: detecção do jogador, perseguição, ataques com cooldown e comportamento de recuo/ataque.
  - Sistema de hitboxes separado da caixa visual (ajustável via `HITBOX_WIDTH` / `HITBOX_HEIGHT`).
  - Sistema de colisões para ataques (área de ataque baseada na hitbox e na direção do jogador).
  - Barra de HP para inimigos e overlay de HP do jogador.
  - Pickups de vida (Health) que reaparecem após um tempo quando coletados.
  - Efeitos de gameplay: slow-motion (pequena redução de time-scale) e zoom momentâneo em impactos.
  - Efeito de impacto (hitspark): pequena animação de 2 frames exibida quando o jogador ou inimigo leva dano.

- Menus e fluxos de UI:
  - Menu de pausa com opções (Continuar, Configuração, Voltar ao Menu).
  - Menu de morte com opção de reiniciar fase ou voltar ao menu.
  - Overlay de configuração (audio/controle) acessível a partir do menu e do pause.

- Gerenciador de áudio avançado (`AudioManager`):
  - Reproduz SFX e músicas a partir de `assets/sounds` e `assets/music`.
  - Suporta carregamento preguiçoso, variantes de SFX (pastas com várias variantes), e processamento de camadas (pitch, bitcrush, distortion) quando numpy está disponível.
  - Crossfade de músicas, ramp-up para música de menu, e playback de músicas de batalha com crossfade entre tracks.


## Controles

- Mover: ← / A (esquerda), → / D (direita)
- Pular: Space / W / ↑
- Atacar: Ctrl esquerdo/direito
- Pausar / Voltar ao menu: Esc
- Navegar menus: ↑/W e ↓/S • Enter para selecionar


## Estrutura de ativos

- `src/assets/images/player/` — spritesheets do jogador (nomes esperados como `_Idle.png`, `_Run.png`, etc.)
- `src/assets/images/enemy/` — spritesheets dos inimigos
- `src/assets/images/health/_Health.png` — asset do pickup de vida
- `src/assets/sounds/` — efeitos sonoros (sfx) e subpastas com variantes
- `src/assets/music/` — trilhas de música (menu, gameplay, game_over)

Créditos dos assets
-------------------

Alguns assets utilizados neste protótipo foram obtidos de coleções gratuitas no itch.io:

- Fantasy Knight (personagem animado) — disponível em: https://aamatniekss.itch.io/fantasy-knight-free-pixelart-animated-character
- Pixel Combat (sfx) — disponível em: https://heltonyan.itch.io/pixelcombat

Assets foram alterados manualmente por mim para se adequarem às necessidades do projeto (recorte, redimensionamento, ajustes de cor).


## Configurações e constantes relevantes

- `src/game/settings.py` contém constantes fundamentais como `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `FPS`, cores, `HITBOX_WIDTH`, `HITBOX_HEIGHT`, `ATTACK_RANGE`, `ATTACK_HEIGHT_FACTOR`. não modifique sem necessidade.


## Como executar

Requisitos mínimos:

- Python 3.8+ (recomendado)
- dependências listadas em `requirements.txt` (principalmente pygame; numpy é opcional para processamento avançado de áudio)

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

O projeto segue a licença MIT (se desejar adicionar um arquivo LICENSE, inclua-o na raiz).