"""
Datos de proveedores conocidos.

Este archivo contiene:
- PROVEEDORES_CONOCIDOS: diccionario con CIF e IBAN de cada proveedor
- CIF_A_PROVEEDOR: diccionario inverso para detectar proveedor por CIF
- EXTRACTOR_PDF_PROVEEDOR: método de extracción PDF por proveedor
- PROVEEDOR_ALIAS: alias para normalización de nombres

Actualizado: 18/12/2025 - v4.0
"""

# =============================================================================
# CONFIGURACIÓN BÁSICA
# =============================================================================

CIF_PROPIO = "B87760575"

# Bancos a evitar en IBAN (cuando hay varios)
BANCOS_EVITAR = ["0049"]

# =============================================================================
# ALIAS DE PROVEEDORES
# =============================================================================

# Para búsqueda en diccionario de categorías
PROVEEDOR_ALIAS_DICCIONARIO = {
    'JAMONES BERNAL': 'EMBUTIDOS BERNAL',
    'BERNAL': 'EMBUTIDOS BERNAL',
}

# Para normalización de nombre en salida
PROVEEDOR_NOMBRE_SALIDA = {
    'JAVIER ALBORES': 'CONTROLPLAGA',
    'JAVIER ARBORES': 'CONTROLPLAGA',
    'ALBORES': 'CONTROLPLAGA',
    'ARBORES': 'CONTROLPLAGA',
}

# =============================================================================
# DATOS DE PROVEEDORES (CIF e IBAN)
# =============================================================================

PROVEEDORES_CONOCIDOS = {
    # --- SERRÍN NO CHAN ---
    'SERRIN': {'cif': 'B87214755', 'iban': 'ES88 0049 6650 1329 1001 8834'},
    'SERRÍN': {'cif': 'B87214755', 'iban': 'ES88 0049 6650 1329 1001 8834'},
    'SERRIN NO CHAN': {'cif': 'B87214755', 'iban': 'ES88 0049 6650 1329 1001 8834'},
    
    # --- FABEIRO ---
    'FABEIRO': {'cif': 'B79992079', 'iban': 'ES70 0182 1292 2202 0150 5065'},
    
    # --- DISTRIBUCIONES LAVAPIES ---
    'LAVAPIES': {'cif': 'F88424072', 'iban': 'ES39 3035 0376 1437 6001 1213'},
    'DISTRIBUCIONES LAVAPIES': {'cif': 'F88424072', 'iban': 'ES39 3035 0376 1437 6001 1213'},
    
    # --- ALQUILERES (personas físicas) ---
    'BENJAMIN ORTEGA': {'cif': '09342596L', 'iban': 'ES31 0049 5977 5521 1606 6585'},
    'ORTEGA ALONSO': {'cif': '09342596L', 'iban': 'ES31 0049 5977 5521 1606 6585'},
    'JAIME FERNANDEZ': {'cif': '07219971H', 'iban': 'ES31 0049 5977 5521 1606 6585'},
    'FERNANDEZ MORENO': {'cif': '07219971H', 'iban': 'ES31 0049 5977 5521 1606 6585'},
    
    # --- SABORES DE PATERNA ---
    'SABORES DE PATERNA': {'cif': 'B96771832', 'iban': 'ES65 2100 8505 1802 0003 1050'},
    'SABORES': {'cif': 'B96771832', 'iban': 'ES65 2100 8505 1802 0003 1050'},
    'PATERNA': {'cif': 'B96771832', 'iban': 'ES65 2100 8505 1802 0003 1050'},
    
    # --- MARTIN ARBENZA / EL MODESTO ---
    'MARTIN ARBENZA': {'cif': '74305431K', 'iban': 'ES37 0049 6193 4128 9534 3887'},
    'MARTIN ABENZA': {'cif': '74305431K', 'iban': 'ES37 0049 6193 4128 9534 3887'},
    'EL MODESTO': {'cif': '74305431K', 'iban': 'ES37 0049 6193 4128 9534 3887'},
    
    # --- FRANCISCO GUERRA ---
    'FRANCISCO GUERRA': {'cif': '50449614B', 'iban': 'ES70 0049 4007 1428 1402 7169'},
    
    # --- TRUCCO / ISAAC RODRIGUEZ ---
    'TRUCCO': {'cif': '05247386M', 'iban': ''},
    'TRUCCO COPIAS': {'cif': '05247386M', 'iban': ''},
    'ISAAC RODRIGUEZ': {'cif': '05247386M', 'iban': ''},
    'ISAAC RODRIGUEZ PACHA': {'cif': '05247386M', 'iban': ''},
    
    # --- ISTA ---
    'ISTA': {'cif': 'A50090133', 'iban': ''},
    
    # --- AMAZON ---
    'AMAZON': {'cif': 'W0184081H', 'iban': ''},
    
    # --- VINOS DE ARGANZA ---
    'VINOS DE ARGANZA': {'cif': 'B24416869', 'iban': 'ES92 0081 5385 6500 0121 7327'},
    'ARGANZA': {'cif': 'B24416869', 'iban': 'ES92 0081 5385 6500 0121 7327'},
    
    # --- LA PURISIMA ---
    'LA PURISIMA': {'cif': 'F30005193', 'iban': 'ES78 0081 0259 1000 0184 4495'},
    'PURISIMA': {'cif': 'F30005193', 'iban': 'ES78 0081 0259 1000 0184 4495'},
    
    # --- MOLLETES ARTESANOS ---
    'MOLLETES': {'cif': 'B93662708', 'iban': 'ES34 0049 4629 5323 1715 7896'},
    'MOLLETES ARTESANOS': {'cif': 'B93662708', 'iban': 'ES34 0049 4629 5323 1715 7896'},
    
    # --- BODEGAS BORBOTON ---
    'BODEGAS BORBOTON': {'cif': 'B45851755', 'iban': 'ES37 2100 1913 1902 0013 5677'},
    'BORBOTON': {'cif': 'B45851755', 'iban': 'ES37 2100 1913 1902 0013 5677'},
    
    # --- LOS GREDALES ---
    'LOS GREDALES': {'cif': 'B83594150', 'iban': 'ES82 2103 7178 2800 3001 2932'},
    'GREDALES': {'cif': 'B83594150', 'iban': 'ES82 2103 7178 2800 3001 2932'},
    'LOS GREDALES DEL TOBOSO': {'cif': 'B83594150', 'iban': 'ES82 2103 7178 2800 3001 2932'},
    
    # --- GADITAUN / María Linarejos ---
    'GADITAUN': {'cif': '34007216Z', 'iban': 'ES19 0081 0259 1000 0163 8268'},
    'MARILINA': {'cif': '34007216Z', 'iban': 'ES19 0081 0259 1000 0163 8268'},
    'MARIA LINAREJOS': {'cif': '34007216Z', 'iban': 'ES19 0081 0259 1000 0163 8268'},
    
    # --- ECOMS / DIA ---
    'ECOMS': {'cif': 'B72738602', 'iban': ''},
    'ECOMS SUPERMARKET': {'cif': 'B72738602', 'iban': ''},
    'DIA': {'cif': 'B72738602', 'iban': ''},
    
    # --- FELISA GOURMET ---
    'FELISA GOURMET': {'cif': 'B72113897', 'iban': 'ES68 0182 1076 9502 0169 3908'},
    'FELISA': {'cif': 'B72113897', 'iban': 'ES68 0182 1076 9502 0169 3908'},
    
    # --- JAMONES BERNAL ---
    'JAMONES BERNAL': {'cif': 'B67784231', 'iban': 'ES49 2100 7191 2902 0003 7620'},
    'BERNAL': {'cif': 'B67784231', 'iban': 'ES49 2100 7191 2902 0003 7620'},
    'EMBUTIDOS BERNAL': {'cif': 'B67784231', 'iban': 'ES49 2100 7191 2902 0003 7620'},
    
    # --- EMJAMESA ---
    'EMJAMESA': {'cif': 'B37352077', 'iban': 'ES08 3016 0206 5221 8503 2527'},
    
    # --- MAKRO ---
    'MAKRO': {'cif': 'A28647451', 'iban': ''},
    
    # --- LA MOLIENDA VERDE ---
    'LA MOLIENDA VERDE': {'cif': 'B06936140', 'iban': 'ES41 3023 0407 1669 9576 7701'},
    'MOLIENDA VERDE': {'cif': 'B06936140', 'iban': 'ES41 3023 0407 1669 9576 7701'},
    
    # --- ZUBELZU ---
    'ZUBELZU': {'cif': 'B75079608', 'iban': 'ES61 3035 0141 8214 1001 9635'},
    'ZUBELZU PIPARRAK': {'cif': 'B75079608', 'iban': 'ES61 3035 0141 8214 1001 9635'},
    
    # --- EL CARRASCAL ---
    'CARRASCAL': {'cif': '07951036M', 'iban': 'ES59 0049 0344 98 2510368354'},
    'EL CARRASCAL': {'cif': '07951036M', 'iban': 'ES59 0049 0344 98 2510368354'},
    'JOSE LUIS SANCHEZ': {'cif': '07951036M', 'iban': 'ES59 0049 0344 98 2510368354'},
    
    # --- SILVA CORDERO ---
    'SILVA CORDERO': {'cif': 'B09861535', 'iban': 'ES48 3001 0050 78 5010003340'},
    'QUESOS SILVA CORDERO': {'cif': 'B09861535', 'iban': 'ES48 3001 0050 78 5010003340'},
    'ACEHUCHE': {'cif': 'B09861535', 'iban': 'ES48 3001 0050 78 5010003340'},
    
    # --- JIMELUZ ---
    'JIMELUZ': {'cif': 'B84527068', 'iban': ''},
    'JIMELUZ EMPRENDEDORES': {'cif': 'B84527068', 'iban': ''},
    
    # --- LA ROSQUILLERIA ---
    'LA ROSQUILLERIA': {'cif': 'B73814949', 'iban': 'ES16 0487 0061 1320 0700 2940'},
    'ROSQUILLERIA': {'cif': 'B73814949', 'iban': 'ES16 0487 0061 1320 0700 2940'},
    
    # --- IBARRAKO PIPARRAK ---
    'IBARRAKO PIPARRAK': {'cif': 'F20532297', 'iban': 'ES69 2095 5081 9010 6181 7077'},
    'IBARRAKO PIPARRA': {'cif': 'F20532297', 'iban': 'ES69 2095 5081 9010 6181 7077'},
    'IBARRAKO': {'cif': 'F20532297', 'iban': 'ES69 2095 5081 9010 6181 7077'},
    
    # --- MANIPULADOS ABELLAN ---
    'MANIPULADOS ABELLAN': {'cif': 'B30473326', 'iban': 'ES06 2100 8321 0413 0018 3503'},
    'ABELLAN': {'cif': 'B30473326', 'iban': 'ES06 2100 8321 0413 0018 3503'},
    'EL LABRADOR': {'cif': 'B30473326', 'iban': 'ES06 2100 8321 0413 0018 3503'},
    
    # --- ZUCCA / FORMAGGIARTE ---
    'ZUCCA': {'cif': 'B42861948', 'iban': 'ES05 1550 0001 2000 1157 7624'},
    'FORMAGGIARTE': {'cif': 'B42861948', 'iban': 'ES05 1550 0001 2000 1157 7624'},
    'QUESERIA ZUCCA': {'cif': 'B42861948', 'iban': 'ES05 1550 0001 2000 1157 7624'},
    
    # --- CVNE ---
    'CVNE': {'cif': 'A48002893', 'iban': 'ES09 2100 9144 3102 0002 5176'},
    'COMPAÑIA VINICOLA': {'cif': 'A48002893', 'iban': 'ES09 2100 9144 3102 0002 5176'},
    
    # --- ADEUDOS (sin IBAN) ---
    'YOIGO': {'cif': 'A82528548', 'iban': ''},
    'XFERA': {'cif': 'A82528548', 'iban': ''},
    'SOM ENERGIA': {'cif': 'F55091367', 'iban': ''},
    'LUCERA': {'cif': 'B98670003', 'iban': ''},
    'SEGURMA': {'cif': 'A48198626', 'iban': ''},
    'KINEMA': {'cif': 'F84600022', 'iban': ''},
    
    # --- MIGUEZ CAL / FORPLAN ---
    'MIGUEZ CAL': {'cif': 'B79868006', 'iban': 'ES96 2085 9748 9203 0003 9285'},
    'FORPLAN': {'cif': 'B79868006', 'iban': 'ES96 2085 9748 9203 0003 9285'},
    
    # --- MARITA COSTA ---
    'MARITA COSTA': {'cif': '48207369J', 'iban': 'ES08 0182 7036 0902 0151 9833'},
    
    # --- PILAR RODRIGUEZ / EL MAJADAL ---
    'PILAR RODRIGUEZ': {'cif': '06582655D', 'iban': 'ES30 5853 0199 2810 0235 62'},
    'EL MAJADAL': {'cif': '06582655D', 'iban': 'ES30 5853 0199 2810 0235 62'},
    'HUEVOS EL MAJADAL': {'cif': '06582655D', 'iban': 'ES30 5853 0199 2810 0235 62'},
    
    # --- PANIFIESTO ---
    'PANIFIESTO': {'cif': 'B87874327', 'iban': ''},
    'PANIFIESTO LAVAPIES': {'cif': 'B87874327', 'iban': ''},
    
    # --- JULIO GARCIA VIVAS ---
    'JULIO GARCIA VIVAS': {'cif': '02869898G', 'iban': ''},
    'GARCIA VIVAS': {'cif': '02869898G', 'iban': ''},
    
    # --- MRM ---
    'MRM': {'cif': 'A80280845', 'iban': 'ES28 2100 8662 5702 0004 8824'},
    'MRM-2': {'cif': 'A80280845', 'iban': 'ES28 2100 8662 5702 0004 8824'},
    'INDUSTRIAS CARNICAS MRM': {'cif': 'A80280845', 'iban': 'ES28 2100 8662 5702 0004 8824'},
    
    # --- DISBER ---
    'DISBER': {'cif': 'B46144424', 'iban': 'ES39 2100 8617 1502 0002 4610'},
    'GRUPO DISBER': {'cif': 'B46144424', 'iban': 'ES39 2100 8617 1502 0002 4610'},
    
    # --- LA BARRA DULCE ---
    'LA BARRA DULCE': {'cif': 'B19981141', 'iban': 'ES76 2100 5606 4802 0017 4138'},
    'BARRA DULCE': {'cif': 'B19981141', 'iban': 'ES76 2100 5606 4802 0017 4138'},
    
    # --- GRUPO CAMPERO ---
    'GRUPO TERRITORIO CAMPERO': {'cif': 'B16690141', 'iban': 'ES71 0049 3739 4027 1401 6466'},
    'TERRITORIO CAMPERO': {'cif': 'B16690141', 'iban': 'ES71 0049 3739 4027 1401 6466'},
    'GRUPO CAMPERO': {'cif': 'B16690141', 'iban': 'ES71 0049 3739 4027 1401 6466'},
    
    # --- PRODUCTOS ADELL ---
    'PRODUCTOS ADELL': {'cif': 'B12711636', 'iban': 'ES62 3058 7413 2127 2000 8367'},
    'CROQUELLANAS': {'cif': 'B12711636', 'iban': 'ES62 3058 7413 2127 2000 8367'},
    
    # --- ECOFICUS ---
    'ECOFICUS': {'cif': 'B10214021', 'iban': 'ES23 2103 7136 4700 3002 4378'},
    
    # --- QUESOS ROYCA ---
    'QUESOS ROYCA': {'cif': 'E06388631', 'iban': ''},
    'COMERCIAL ROYCA': {'cif': 'E06388631', 'iban': ''},
    'ROYCA': {'cif': 'E06388631', 'iban': ''},
    
    # --- ANA CABALLO ---
    'ANA CABALLO': {'cif': 'B87925970', 'iban': 'ES75 2100 1360 2202 0006 0355'},
    'ANA CABALLO VERMOUTH': {'cif': 'B87925970', 'iban': 'ES75 2100 1360 2202 0006 0355'},
    
    # --- QUESOS FELIX ---
    'QUESOS FELIX': {'cif': 'B47440136', 'iban': 'ES40 2103 4346 3300 3306 5431'},
    'ARMANDO SANZ': {'cif': 'B47440136', 'iban': 'ES40 2103 4346 3300 3306 5431'},
    'FELIX': {'cif': 'B47440136', 'iban': 'ES40 2103 4346 3300 3306 5431'},
    
    # --- PANRUJE ---
    'PANRUJE': {'cif': 'B13858014', 'iban': 'ES19 0081 5344 2800 0261 4066'},
    'ROSQUILLAS LA ERMITA': {'cif': 'B13858014', 'iban': 'ES19 0081 5344 2800 0261 4066'},
    'LA ERMITA': {'cif': 'B13858014', 'iban': 'ES19 0081 5344 2800 0261 4066'},
    
    # --- CARLOS NAVAS ---
    'CARLOS NAVAS': {'cif': 'B37416419', 'iban': 'ES62 2100 6153 0402 0001 6597'},
    'QUESERIA CARLOS NAVAS': {'cif': 'B37416419', 'iban': 'ES62 2100 6153 0402 0001 6597'},
    'QUESERIA NAVAS': {'cif': 'B37416419', 'iban': 'ES62 2100 6153 0402 0001 6597'},
    'QUESOS NAVAS': {'cif': 'B37416419', 'iban': 'ES62 2100 6153 0402 0001 6597'},
    
    # --- PORVAZ ---
    'PORVAZ': {'cif': 'B36281087', 'iban': 'ES63 0049 5368 0625 1628 3321'},
    'PORVAZ VILAGARCIA': {'cif': 'B36281087', 'iban': 'ES63 0049 5368 0625 1628 3321'},
    'CONSERVAS TITO': {'cif': 'B36281087', 'iban': 'ES63 0049 5368 0625 1628 3321'},
    'TITO': {'cif': 'B36281087', 'iban': 'ES63 0049 5368 0625 1628 3321'},
    
    # --- CONTROLPLAGA ---
    'CONTROLPLAGA': {'cif': '11812266H', 'iban': 'ES86 0081 7122 58 0001218325'},
    'JAVIER ALBORES': {'cif': '11812266H', 'iban': 'ES86 0081 7122 58 0001218325'},
    'JAVIER ARBORES': {'cif': '11812266H', 'iban': 'ES86 0081 7122 58 0001218325'},
    
    # --- ANGEL Y LOLI ---
    'ANGEL Y LOLI': {'cif': '75727068M', 'iban': ''},
    'ALFARERIA ANGEL': {'cif': '75727068M', 'iban': ''},
    
    # --- QUESOS DEL CATI ---
    'QUESOS DEL CATI': {'cif': 'F12499455', 'iban': 'ES89 2100 7363 72 1100030799'},
    'QUESOS CATI': {'cif': 'F12499455', 'iban': 'ES89 2100 7363 72 1100030799'},
    
    # --- BIELLEBI ---
    'BIELLEBI': {'cif': '06089700725', 'iban': 'IT68B0306941603100000001003'},
    'BIELLEBI SRL': {'cif': '06089700725', 'iban': 'IT68B0306941603100000001003'},
    
    # --- FERRIOL ---
    'EMBUTIDOS FERRIOL': {'cif': 'B57955098', 'iban': 'ES22 2100 0088 0502 0014 6500'},
    'EMBOTITS FERRIOL': {'cif': 'B57955098', 'iban': 'ES22 2100 0088 0502 0014 6500'},
    'FERRIOL': {'cif': 'B57955098', 'iban': 'ES22 2100 0088 0502 0014 6500'},
    
    # --- ABBATI ---
    'ABBATI CAFFE': {'cif': 'B82567876', 'iban': ''},
    'ABBATI': {'cif': 'B82567876', 'iban': ''},
    
    # --- BODEGAS MUÑOZ MARTIN ---
    'BODEGAS MUÑOZ MARTIN': {'cif': 'E83182683', 'iban': 'ES62 0049 5184 11 2016002766'},
    'MUÑOZ MARTIN': {'cif': 'E83182683', 'iban': 'ES62 0049 5184 11 2016002766'},
    
    # --- CERES ---
    'CERES': {'cif': 'B83478669', 'iban': ''},
    'CERES CERVEZA': {'cif': 'B83478669', 'iban': ''},
    
    # --- BERZAL ---
    'BERZAL': {'cif': 'A78490182', 'iban': 'ES75 0049 1500 0520 1004 9174'},
    'BERZAL HERMANOS': {'cif': 'A78490182', 'iban': 'ES75 0049 1500 0520 1004 9174'},
    
    # --- BM SUPERMERCADOS ---
    'BM': {'cif': 'B20099586', 'iban': ''},
    'BM SUPERMERCADOS': {'cif': 'B20099586', 'iban': ''},
    
    # --- LIDL ---
    'LIDL': {'cif': 'A60195278', 'iban': ''},
    
    # --- PC COMPONENTES ---
    'PC COMPONENTES': {'cif': 'B73347494', 'iban': ''},
    
    # --- LICORES MADRUEÑO ---
    'LICORES MADRUEÑO': {'cif': 'B86705126', 'iban': 'ES78 0081 0259 1000 0184 4495'},
    'MADRUEÑO': {'cif': 'B86705126', 'iban': 'ES78 0081 0259 1000 0184 4495'},
}


# =============================================================================
# DICCIONARIO INVERSO CIF → PROVEEDOR
# =============================================================================

CIF_A_PROVEEDOR = {
    'B83478669': 'CERES',
    'B87214755': 'SERRIN',
    'B79992079': 'FABEIRO',
    'F88424072': 'DISTRIBUCIONES LAVAPIES',
    '09342596L': 'BENJAMIN ORTEGA',
    '07219971H': 'JAIME FERNANDEZ',
    'B96771832': 'SABORES DE PATERNA',
    '74305431K': 'MARTIN ABENZA',
    '50449614B': 'FRANCISCO GUERRA',
    '05247386M': 'TRUCCO',
    'A50090133': 'ISTA',
    'W0184081H': 'AMAZON',
    'B24416869': 'VINOS DE ARGANZA',
    'F30005193': 'LA PURISIMA',
    'B93662708': 'MOLLETES ARTESANOS',
    'B45851755': 'BORBOTON',
    'B83594150': 'LOS GREDALES',
    '34007216Z': 'GADITAUN',
    'B72738602': 'ECOMS',
    'B72113897': 'FELISA',
    'B67784231': 'JAMONES BERNAL',
    'B37352077': 'EMJAMESA',
    'A28647451': 'MAKRO',
    'B42861948': 'ZUCCA',
    'A48002893': 'CVNE',
    'A82528548': 'YOIGO',
    'F55091367': 'SOM ENERGIA',
    'B98670003': 'LUCERA',
    'A48198626': 'SEGURMA',
    'F84600022': 'KINEMA',
    'B79868006': 'MIGUEZ CAL',
    '48207369J': 'MARITA COSTA',
    '06582655D': 'PILAR RODRIGUEZ',
    'B87874327': 'PANIFIESTO',
    '02869898G': 'JULIO GARCIA VIVAS',
    'A80280845': 'MRM',
    'B46144424': 'DISBER',
    'B19981141': 'LA BARRA DULCE',
    'B16690141': 'GRUPO CAMPERO',
    'B75079608': 'ZUBELZU',
    'B12711636': 'PRODUCTOS ADELL',
    'B10214021': 'ECOFICUS',
    'E06388631': 'QUESOS ROYCA',
    'F20532297': 'IBARRAKO PIPARRAK',
    'B87925970': 'ANA CABALLO',
    'B47440136': 'QUESOS FELIX',
    'B13858014': 'PANRUJE',
    'B37416419': 'CARLOS NAVAS',
    'B36281087': 'PORVAZ',
    '11812266H': 'CONTROLPLAGA',
    '75727068M': 'ANGEL Y LOLI',
    'F12499455': 'QUESOS DEL CATI',
    '06089700725': 'BIELLEBI',
    'B57955098': 'FERRIOL',
    'B82567876': 'ABBATI CAFE',
    'E83182683': 'BODEGAS MUÑOZ MARTIN',
    'A78490182': 'BERZAL',
    'B20099586': 'BM SUPERMERCADOS',
    'A60195278': 'LIDL',
    'B73347494': 'PC COMPONENTES',
    'B06936140': 'LA MOLIENDA VERDE',
    'B84527068': 'JIMELUZ',
    'B73814949': 'LA ROSQUILLERIA',
    'B30473326': 'MANIPULADOS ABELLAN',
    'B09861535': 'SILVA CORDERO',
    '07951036M': 'EL CARRASCAL',
    'B86705126': 'LICORES MADRUEÑO',
}


# =============================================================================
# MÉTODO DE EXTRACCIÓN PDF POR PROVEEDOR
# =============================================================================

EXTRACTOR_PDF_PROVEEDOR = {
    # Proveedores que funcionan mejor con pdfplumber
    'CERES': 'pdfplumber',
    'BODEGAS BORBOTON': 'pdfplumber',
    'BORBOTON': 'pdfplumber',
    'FELISA GOURMET': 'pdfplumber',
    'FELISA': 'pdfplumber',
    'DISTRIBUCIONES LAVAPIES': 'pdfplumber',
    'LAVAPIES': 'pdfplumber',
    'LIDL': 'pdfplumber',
    'BODEGAS MUÑOZ MARTIN': 'pdfplumber',
    'MUÑOZ MARTIN': 'pdfplumber',
    'EMJAMESA': 'pdfplumber',
    'MOLIENDA VERDE': 'pdfplumber',
    'LA MOLIENDA VERDE': 'pdfplumber',
    'ZUBELZU': 'pdfplumber',
    'IBARRAKO PIPARRAK': 'pdfplumber',
    'IBARRAKO PIPARRA': 'pdfplumber',
    'IBARRAKO': 'pdfplumber',
    
    # Proveedores OCR (PDFs escaneados)
    'JIMELUZ': 'ocr',
    'LA ROSQUILLERIA': 'ocr',
    'ROSQUILLERIA': 'ocr',
    'MANIPULADOS ABELLAN': 'ocr',
    'FISHGOURMET': 'ocr',
    'MARIA LINAREJOS': 'ocr',
}


def obtener_datos_proveedor(nombre: str) -> dict:
    """
    Obtiene CIF e IBAN de un proveedor.
    
    Args:
        nombre: Nombre del proveedor
        
    Returns:
        {'cif': '...', 'iban': '...'} o {'cif': '', 'iban': ''} si no existe
    """
    nombre_upper = nombre.upper()
    
    # Buscar coincidencia exacta
    if nombre_upper in PROVEEDORES_CONOCIDOS:
        return PROVEEDORES_CONOCIDOS[nombre_upper]
    
    # Buscar coincidencia parcial
    for clave, datos in PROVEEDORES_CONOCIDOS.items():
        if clave in nombre_upper or nombre_upper in clave:
            return datos
    
    return {'cif': '', 'iban': ''}


def obtener_proveedor_por_cif(cif: str) -> str:
    """
    Obtiene el nombre del proveedor a partir de su CIF.
    
    Args:
        cif: CIF del proveedor
        
    Returns:
        Nombre del proveedor o cadena vacía si no existe
    """
    # Limpiar CIF
    cif_limpio = cif.replace('-', '').replace(' ', '').upper()
    
    return CIF_A_PROVEEDOR.get(cif_limpio, '')


def obtener_metodo_pdf(proveedor: str) -> str:
    """
    Obtiene el método de extracción PDF para un proveedor.
    
    Args:
        proveedor: Nombre del proveedor
        
    Returns:
        'pypdf', 'pdfplumber' u 'ocr'
    """
    proveedor_upper = proveedor.upper()
    
    return EXTRACTOR_PDF_PROVEEDOR.get(proveedor_upper, 'pypdf')
