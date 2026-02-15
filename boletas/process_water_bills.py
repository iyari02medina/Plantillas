import pandas as pd
from datetime import datetime
import locale

# Set locale to Spanish for month names
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES')
    except locale.Error:
        # Fallback if system doesn't support Spanish locale directly, we'll handle month names manually
        pass

def get_month_name(date_obj):
    # Custom logic for month determination
    # If day is 25-31: Current month
    # If day is 1-5: Previous month
    
    day = date_obj.day
    month = date_obj.month
    year = date_obj.year
    
    target_month = month
    target_year = year
    
    if 1 <= day <= 5:
        # Previous month
        if month == 1:
            target_month = 12
            target_year = year - 1
        else:
            target_month = month - 1
    # else (day >= 25 or others): use current month
    
    # Map month number to Spanish name
    months = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    return months[target_month]

def process_bills():
    input_file = 'Consumos_agua_Excedentes_Contaminantes.csv'
    output_file = 'V2_Consumos_agua_Excedentes_Contaminantes.csv'
    
    # Paying locales list
    paying_locales = [
        4, 13, 22, 23, 24, 104, 108, 112, 114, 115, 117, 118, 119, 129, 
        209, 210, 214, 216, 302, 303, 320, 322, 323, 325, 326, 401
    ]
    
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
        return

    # Convert fecha_lectura to datetime objects
    # Assuming format DD/MM/YYYY based on file view
    df['fecha_lectura_dt'] = pd.to_datetime(df['fecha_lectura'], format='%d/%m/%Y')
    
    # Sort by Local and Date to calculate consumption
    df = df.sort_values(by=['Local', 'fecha_lectura_dt'])
    
    # Calculate previous reading and consumption
    # We group by Local and shift to get the previous row's reading
    df['lectura_anterior'] = df.groupby('Local')['lectura'].shift(1)
    
    # Fill NaN for first readings (consumption 0 or just current reading? Usually 0 if no previous)
    # But wait, if it's the first reading ever, consumption might be 0 or undefined. 
    # Let's assume consumption = 0 if no previous reading exists in this file.
    # df['lectura_anterior'] = df['lectura_anterior'].fillna(0) # Removed to keep blank if missing 
    
    # However, if the file contains history, the first row for a local is the starting point.
    # If we want to calculate consumption for that first row, we need a previous reading which we don't have.
    # Usually in these files, we might want to skip the very first record per local or set consumption to 0.
    # Let's set consumption = current - previous. If previous is 0 (filled), consumption = current.
    # But if it's a running log, the first entry might be just a baseline. 
    # Let's calculate it, but for the very first entry of each local in the file, 
    # if we treat fillna(0), consumption = reading. This might be wrong if the meter didn't start at 0.
    # Let's check if we should just leave it as NaN or 0.
    # For now, let's calculate it.
    
    df['consumo'] = df['lectura'] - df['lectura_anterior']
    
    # If consumption is negative (meter reset?), handle it? 
    # Assuming standard incrementing meter.
    # For the first record of each group, consumption will be the full reading value (since prev is 0).
    # This might be high. But without historical data outside this file, it's the best we can do.
    # Alternatively, we could set consumption to 0 for the first record if we don't want to bill the initial reading as full consumption.
    # Given the user prompt "lectura actual menos la anterior", implies we need an 'anterior'.
    # I will set consumption to 0 for the first record of each local to avoid massive bills for the baseline.
    
    # Identify first record per local
    # is_first = df.groupby('Local').cumcount() == 0
    # df.loc[is_first, 'consumo'] = 0 # Removed to keep blank if missing
    
    # Calculate month name
    df['mes_consumo'] = df['fecha_lectura_dt'].apply(get_month_name)
    
    # Pricing constants
    PRECIO_M3 = 74
    IVA_RATE = 0.16
    
    # Calculate prices
    # Only for "plaza kentro" as per prompt? 
    # Prompt says: 'El precio_m3 para todos los que dicen "plaza kentro" sera de $70'
    # The file has a 'Plaza' column.
    
    def calculate_row(row):
        # Check if paying local
        if row['Local'] not in paying_locales:
            return pd.Series([None, None, None, None, ""]) # precio_m3, precio, iva, total, cuota_boleta - Blank cells
        
        # Check plaza name (case insensitive just in case)
        if str(row['Plaza']).lower().strip() == 'plaza kentro':
            p_m3 = PRECIO_M3
        else:
            # What if it's not plaza kentro? Prompt didn't specify, assume 0 or keep same?
            # Prompt implies specific price for that plaza. I'll assume 0 or standard if others exist.
            # Looking at the CSV, all seem to be "plaza kentro".
            p_m3 = None # Blank if not plaza kentro 
            
        if p_m3 is None:
             return pd.Series([None, None, None, None, ""])

        precio = row['consumo'] * p_m3
        
        # Apply minimum price of 650 for those with excedentes contaminants (paying_locales)
        if precio <= 650:
            precio = 650
            cuota_boleta = "Tarifa Mínima Fija: "
        else:
            cuota_boleta = "Costo m3 por contaminantes: "
            
        iva = precio * IVA_RATE
        total = precio + iva
        
        return pd.Series([p_m3, precio, iva, total, cuota_boleta])

    # Apply calculation
    price_cols = df.apply(calculate_row, axis=1)
    price_cols.columns = ['precio_m3', 'precio', 'iva', 'precio_total', 'cuota_boleta']
    
    # Join back
    df = pd.concat([df, price_cols], axis=1)
    
    # Concepto pago
    df['concepto_pago'] = "L-" + df['Local'].astype(str) + "-" + df['mes_consumo']
    
    # Select and rename columns for output
    # The user didn't specify exact output columns, but usually we want the calculated ones + identifiers.
    # Let's keep the structure similar to V2 or just add the new columns.
    # Let's output: Plaza, Nombre, Local, fecha_lectura, lectura, lectura_anterior, consumo, mes_consumo, precio_m3, precio, iva, precio_total, concepto_pago
    
    # Determine excedentes_contaminantes
    df['excedentes_contaminantes'] = df['Local'].apply(lambda x: 'si' if x in paying_locales else 'no')

    output_columns = [
        'Plaza', 'Nombre', 'Local', 'fecha_lectura', 'lectura', 
        'lectura_anterior', 'consumo', 'mes_consumo', 
        'excedentes_contaminantes',
        'precio_m3', 'precio', 'iva', 'precio_total', 'cuota_boleta', 'concepto_pago'
    ]
    
    df_out = df[output_columns]
    
    # Round monetary values to 2 decimals
    cols_to_round = ['lectura', 'lectura_anterior', 'consumo', 'precio', 'iva', 'precio_total']
    df_out[cols_to_round] = df_out[cols_to_round].round(2)
    
    df_out.to_csv(output_file, index=False)
    print(f"Successfully created {output_file}")

if __name__ == "__main__":
    process_bills()
