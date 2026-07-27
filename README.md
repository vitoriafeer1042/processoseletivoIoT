# Relatório do Candidato - Contador de Produção Não-Intrusivo

## Identificação do Candidato
- **Nome completo:** Vitória Fernandes
- **GitHub:** vitoriafeer1042

## Visão Geral da Solução
- **Qual é o objetivo do projeto:** Desenvolver uma solução de baixo custo para monitoramento e contagem de peças em linhas de montagem, substituindo a necessidade de um CLP tradicional e evitando a anotação manual.
- **O que o sistema embarcado simulado faz:** O sistema monitora as variações de luminosidade utilizando um sensor óptico LDR. Ele identifica a passagem de itens (incrementando um contador geral), aponta possíveis travamentos da esteira (micro-paradas) caso a luz permaneça bloqueada por muito tempo, e emite logs na porta serial para acompanhamento.
- **Como o usuário interage com ele:** O operador visualiza as contagens e os alertas de parada via console serial. Além disso, pode acionar o botão de "Reset de Turno" para zerar todas as variáveis e preparar o sistema para um novo lote.

## Arquitetura do Sistema Embarcado
A solução adota uma abordagem assíncrona baseada em polling, permitindo o funcionamento paralelo de múltiplas verificações sem interromper o hardware principal.

- **Fluxo principal (`main.py`):** O código executa um laço `while True` com uma taxa de varredura regular (`sleep_ms(50)`). Em cada iteração, ele coleta amostras do estado atual, analisa as bordas lógicas e atua caso critérios de transição sejam cumpridos.
- **Estrutura de estados:** 
  - **Espera / Contagem:** Armazena um flag booleano de "bloqueio". A passagem da peça é registrada na "borda de subida" (transição de escuro (< 100 lux) para claro (> 500 lux)), confirmando que o objeto atravessou todo o campo do sensor.
  - **Temporizações (Timer Não-Bloqueante):** Utiliza o `time.ticks_ms()` e o `time.ticks_diff()` para rastrear o tempo gasto sob baixa luminosidade, ativando um alerta se a janela ultrapassar 5 segundos (5000ms), sem utilizar _delays_ que pausariam outras verificações.

## Componentes Utilizados na Simulação
No arquivo `diagram.json`, os seguintes componentes foram integrados:
- **ESP32 DevKit C v4 (`esp`):** Microcontrolador responsável por todo o processamento computacional da simulação em MicroPython e interface serial.
- **Sensor Óptico LDR (`ldr1`):** Conectado com o pino de leitura analógica 34. Transforma o nível de luz do ambiente (lux) em um sinal de variação de tensão compreendido entre 0 e 3.3V, utilizado para reconhecer quando o feixe é obstruído.
- **Push Button (`btn1`):** Conectado ao pino 14 e aterrado. Serve como o controlador de _reset_. Utilizou-se o recurso de _Pull-Up_ interno do ESP32, de forma que o pino lê "1" enquanto inativo e "0" quando acionado pelo operador.

## Decisões Técnicas Relevantes
- **Processamento de Lux:** Foi incluída a lógica matemática baseada nas curvas características (Gamma=0.7 e RL10=50k) do modelo do fotorresistor (LDR) no simulador. Isso garante que a comparação numérica das exigências (ex: > 500 lux e < 100 lux) reflita a física real e corresponda exata e matematicamente às injeções automatizadas pela validação de CI do Wokwi.
- **Controle de Debounce por Software:** Em vez de confiar cegamente nas bordas puras do pino 14, foi implementada uma malha que registra o diferencial de tempo contra um `last_btn_time`. O comando só é aceito se a transição para estado "pressionado" se sustentar, evitando contagens de zeramentos duplicados.
- **Lógica de Flags Independentes:** O alerta de micro-parada utiliza uma variável de controle (`micro_stop_alerted`) que só se reinicia se o bloqueio acabar. Isso evita repetidos envios da string `"Alerta: Micro-parada detectada!"` durante um engarrafamento muito longo.

## Resultados Obtidos
- **Comportamento Final:** O protótipo se comporta com sucesso. A detecção converte corretamente os intervalos analógicos gerados pelo sensor LDR nas instâncias de bloqueio físico. 
- **Requisitos Atendidos:** O sistema incrementa peças, avisa micro-paradas após 5s corretamente, debounca o botão de reset e usa as impressões exatas (case-sensitive) de terminal requisitadas pelo roteiro de correção automatizada.
- **Resultado no Wokwi:** O funcionamento é suave, sem gargalos e a contagem se dá exclusivamente após a caixa terminar de cruzar a linha do sensor, garantindo fidelidade de ciclo e métrica impecável.
