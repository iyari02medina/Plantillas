import csv, os

path = r'C:\Users\DELL\Desktop\Cophi\Recursos\Programa_cophi\Plantillas\inventario\empresas.csv'
temp_path = path + '.tmp'

rows = []
fieldnames = []

# Try multiple encodings
for enc in ['utf-8-sig', 'latin-1', 'cp1252']:
    try:
        with open(path, 'r', encoding=enc) as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        print(f'Successfully read with {enc}')
        break
    except Exception as e:
        print(f'Failed with {enc}: {e}')
        continue

if not rows:
    print('Could not read file.')
    exit(1)

max_id_num = 0
for r in rows:
    id_val = r.get('id_cliente', '')
    if id_val and id_val.startswith('CLI-'):
        try:
            # Extract number from CLI-XXX
            num_str = id_val.split('-')[1]
            num = int(num_str)
            if num > max_id_num: max_id_num = num
        except: pass

updated = False
for r in rows:
    if not r.get('id_cliente'):
        max_id_num += 1
        r['id_cliente'] = f'CLI-{max_id_num:03d}'
        updated = True

if updated:
    with open(temp_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp_path, path)
    print('IDs updated successfully')
else:
    print('No missing IDs found')
