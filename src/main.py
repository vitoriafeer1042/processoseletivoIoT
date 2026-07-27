import machine
import time
import math

print("Contador de Producao Inicializado")

# Setup pins
ldr_pin = machine.ADC(machine.Pin(34))
ldr_pin.atten(machine.ADC.ATTN_11DB) # Full range: 0-3.3v

btn1 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

# Global variables
total_pieces = 0
is_blocked = False
block_start_time = 0
micro_stop_alerted = False
last_btn_state = 1
last_btn_time = 0

def get_lux(adc_val):
    if adc_val == 0:
        return 100000
    if adc_val == 4095:
        return 0.1
    try:
        r_ldr = 10000 * (4095 / adc_val - 1)
        if r_ldr <= 0:
            return 100000
        lux = 10 * math.pow(50000 / r_ldr, 1 / 0.7)
        return lux
    except:
        return 0

while True:
    current_time = time.ticks_ms()
    
    # 1. Handle LDR reading
    adc_val = ldr_pin.read()
    lux = get_lux(adc_val)
    
    # 2. Logic for detection
    if not is_blocked and lux < 100:
        is_blocked = True
        block_start_time = current_time
        micro_stop_alerted = False
    elif is_blocked and lux > 500:
        is_blocked = False
        total_pieces += 1
        print("Peca detectada! Total: {}".format(total_pieces))
        
    # 3. Logic for Micro-stop (lux < 100 for > 5 seconds)
    if is_blocked and not micro_stop_alerted:
        if time.ticks_diff(current_time, block_start_time) > 5000:
            print("Alerta: Micro-parada detectada!")
            micro_stop_alerted = True
            
    # 4. Handle Button for Reset
    btn_state = btn1.value()
    # Debounce
    if btn_state != last_btn_state and time.ticks_diff(current_time, last_btn_time) > 50:
        if btn_state == 0: # Pressed
            total_pieces = 0
            is_blocked = False
            micro_stop_alerted = False
            print("Turno resetado com sucesso. Contadores zerados.")
        last_btn_state = btn_state
        last_btn_time = current_time
            
    time.sleep_ms(50) # Non-blocking delay
