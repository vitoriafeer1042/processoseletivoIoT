import machine
import time

# Configuracao de pinos
pino_sensor = machine.ADC(machine.Pin(34))
pino_sensor.atten(machine.ADC.ATTN_11DB)
pino_sensor.width(machine.ADC.WIDTH_12BIT)

pino_botao = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

# Limiares de deteccao (valores brutos do ADC)
# No modulo LDR do Wokwi: escuro = ADC alto, claro = ADC baixo
ADC_ESCURO = 2000    # Acima disso: objeto bloqueando o sensor
ADC_CLARO = 1000     # Abaixo disso: caminho livre

# Temporizadores
LIMITE_MICRO_PARADA = 5000  # ms sem movimento = micro-parada
DEBOUNCE_MS = 50

# Estado do sistema
pecas_contadas = 0
obstruido = False
inicio_obstrucao = 0
alerta_emitido = False

# Estado do botao
estado_botao_ant = 1
tempo_botao_ant = 0

print("Contador de Producao Inicializado")

while True:
    agora = time.ticks_ms()

    # Leitura do sensor de luminosidade (valor bruto do ADC)
    leitura_adc = pino_sensor.read()

    # Deteccao de pecas por transicao de luminosidade
    if not obstruido and leitura_adc > ADC_ESCURO:
        # Transicao claro -> escuro: objeto entrou na frente do sensor
        obstruido = True
        inicio_obstrucao = agora
        alerta_emitido = False
    elif obstruido and leitura_adc < ADC_CLARO:
        # Transicao escuro -> claro: objeto passou completamente
        obstruido = False
        pecas_contadas += 1
        print("Peca detectada! Total: {}".format(pecas_contadas))

    # Verificacao de micro-parada (sensor bloqueado por tempo excessivo)
    if obstruido and not alerta_emitido:
        if time.ticks_diff(agora, inicio_obstrucao) > LIMITE_MICRO_PARADA:
            print("Alerta: Micro-parada detectada!")
            alerta_emitido = True

    # Leitura do botao de reset com debounce
    estado_botao = pino_botao.value()
    if estado_botao != estado_botao_ant:
        if time.ticks_diff(agora, tempo_botao_ant) > DEBOUNCE_MS:
            if estado_botao == 0:
                pecas_contadas = 0
                obstruido = False
                alerta_emitido = False
                print("Turno resetado com sucesso. Contadores zerados.")
            estado_botao_ant = estado_botao
            tempo_botao_ant = agora

    time.sleep_ms(50)
