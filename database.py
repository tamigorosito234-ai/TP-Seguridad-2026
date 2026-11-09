import sqlite3

DATABASE = 'afinar.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS usuarios')
    cur.execute('DROP TABLE IF EXISTS productos')

    cur.execute('''
        CREATE TABLE usuarios (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            email    TEXT,
            rol      TEXT DEFAULT 'cliente'
        )
    ''')

    cur.execute('''
        CREATE TABLE productos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT    NOT NULL,
            descripcion TEXT,
            categoria   TEXT,
            precio      REAL,
            stock       INTEGER,
            imagen_url  TEXT
        )
    ''')

    usuarios = [
        ('giorgi_l',   'lorenzo2026',  'lorgiorgi@gmail.com',      'admin'),
        ('franco_m',   'franco2026',   'franco.martina@gmail.com',  'cliente'),
        ('rojo_r',     'rojo2026',     'roberto.rojo@gmail.com',    'cliente'),
        ('gorosito_t', 'tamara2026',   'gorosito.t@gmail.com',      'cliente'),
        ('crespin_s',  'sasha2026',    'crespin.sasha@gmail.com',   'cliente'),
    ]
    cur.executemany(
        'INSERT INTO usuarios (username, password, email, rol) VALUES (?, ?, ?, ?)',
        usuarios
    )

    productos = [
        # Guitarras
        ('Guitarra Electrica Stratocaster',
         'Guitarra electrica tipo Strat con cuerpo de aliso, mastil de arce y 3 microfonos single coil. Incluye cable y correa.',
         'Guitarras', 498000, 5,
         '/static/img/guitarraElectricaStrato.jpg'),
        ('Guitarra Electrica Les Paul',
         'Cuerpo de caoba, tapa de arce flameado, 2 humbuckers. Sonido calido y potente, ideal para rock y blues.',
         'Guitarras', 725000, 3,
         '/static/img/guitarraElectricaLesPaul.jpg'),
        ('Guitarra Acustica Dreadnought',
         'Tapa de abeto solido, fondo y aros de caoba. Ideal para folklore y rock acustico. Incluye funda.',
         'Guitarras', 312000, 7,
         '/static/img/guitarraAcusticaDread.jpg'),
        ('Guitarra Clasica 4/4',
         'Tapa de cedro, cuerpo de caoba, cuerdas de nylon. Para estudio y concierto. Ideal para principiantes.',
         'Guitarras', 168000, 10,
         '/static/img/guitarraAcustica.jpg'),
        # Bajos
        ('Bajo Electrico Jazz Bass',
         'Bajo de 4 cuerdas, cuerpo de aliso, mastil de arce, 2 single coils. Versatil y dinamico.',
         'Bajos', 455000, 4,
         '/static/img/bajoElectricoJazz.jpg'),
        ('Bajo Electrico Precision',
         'Bajo clasico de 4 cuerdas con split-coil humbucker. El estandar de la industria desde 1951.',
         'Bajos', 398000, 3,
         '/static/img/bajoElectricoPrecision.jpg'),
        # Teclados
        ('Teclado MIDI 61 teclas',
         'Controlador MIDI de 61 teclas semipesadas, 8 pads de percusion, USB/MIDI. Ideal para produccion.',
         'Teclados', 234000, 6,
         '/static/img/tecladoMIDI61.jpg'),
        ('Piano Digital 88 teclas',
         'Piano digital con accion martillo, 88 teclas pesadas, 256 voces polifonicas. Sonido realista.',
         'Teclados', 1180000, 2,
         '/static/img/pianoDigital88.jpg'),
        ('Sintetizador Analogico',
         'Synth monovoz de 32 teclas, osciladores analogicos, filtro Moog-style. Sonido vintage inigualable.',
         'Teclados', 890000, 2,
         '/static/img/sintetizadorAnalogico.jpg'),
        # Percusion
        ('Bateria Acustica 5 piezas',
         'Set completo: bombo 22", caja 14", 3 toms, charles, platillos crash y ride. Listo para tocar.',
         'Percusion', 2350000, 1,
         '/static/img/bateriaAcustica5.jpg'),
        ('Bateria Electronica 8 pads',
         'Modulo con 8 pads de malla, 600 sonidos, entrada USB, auriculares incluidos. Ideal para practicar.',
         'Percusion', 645000, 3,
         '/static/img/bateriaElec8.jpg'),
        ('Cajon Peruano',
         'Cajon flamenco de madera de abedul, interior con cuerdas regulables. Funda incluida.',
         'Percusion', 118000, 8,
         '/static/img/cajonPeruano.jpg'),
        # Accesorios
        ('Cuerdas Guitarra Electrica 09-42',
         'Set de 6 cuerdas de acero niquelado, calibre 09-42. Pack x3 juegos. Larga duracion.',
         'Accesorios', 9800, 50,
         '/static/img/cuerdasElectrica942.jpg'),
        ('Cuerdas Guitarra Acustica 11-52',
         'Set de 6 cuerdas de bronce fosforado, calibre 11-52. Sonido brillante y proyeccion superior.',
         'Accesorios', 11500, 40,
         '/static/img/cuerdasAcustica1152.jpg'),
        ('Cuerdas Bajo 45-105',
         'Set de 4 cuerdas de acero niquelado para bajo electrico, calibre 45-105. Pack x2 juegos.',
         'Accesorios', 16900, 30,
         '/static/img/cuerdasBajo45105.jpg'),
        ('Puas variadas Pack x24',
         'Pack de 24 puas surtidas: 0.46mm, 0.73mm, 1.00mm, 1.14mm. Varios colores y materiales.',
         'Accesorios', 4200, 100,
         '/static/img/puasx24.jpg'),
        ('Afinador Cromatico Clip-On',
         'Afinador con pantalla LCD giratoria 360 grados, modo cromatico, para todo tipo de instrumento.',
         'Accesorios', 7800, 60,
         '/static/img/afinadorClipOn.jpg'),
        ('Capo para Guitarra',
         'Capo de aluminio con resorte de alta presion. Compatible con guitarra acustica y electrica.',
         'Accesorios', 6500, 45,
         '/static/img/capoGuitarra.jpg'),
        ('Soporte de Guitarra de Pie',
         'Soporte universal plegable para guitarra electrica y acustica. Base antideslizante, facil de armar.',
         'Accesorios', 14900, 25,
         '/static/img/soporteGuitarraPie.jpg'),
        ('Estuche Rigido Guitarra Electrica',
         'Estuche rigido con interior acolchado, cierre doble y herrajes metalicos. Proteccion maxima.',
         'Accesorios', 78000, 10,
         '/static/img/estucheRigidoElectrica.jpg'),
        ('Funda Guitarra Acustica',
         'Funda acolchada con bolsillos laterales, correa para hombro, resistente al agua.',
         'Accesorios', 28500, 20,
         '/static/img/fundaGuitarraAcustica.jpg'),
        ('Correa de Cuero Guitarra',
         'Correa artesanal de cuero genuino, 60-120 cm ajustable, con diseno grabado. Hecha a mano.',
         'Accesorios', 24000, 15,
         '/static/img/correaGuitarra.jpg'),
        ('Clavijero Mecanico 3+3',
         'Set de clavijeros cromados 3+3 para guitarra acustica y electrica. Alta precision y suavidad.',
         'Accesorios', 19500, 20,
         '/static/img/clavijero3+3.jpg'),
        ('Atril de Partituras',
         'Atril metalico plegable, regulable en altura y angulo. Ideal para ensayo y concierto.',
         'Accesorios', 13200, 18,
         '/static/img/atrilPartituras.jpg'),
        ('Metronomo Digital',
         'Metronomo con pantalla LCD, 30-250 BPM, tap tempo, entrada auriculares. Imprescindible para practicar.',
         'Accesorios', 17400, 22,
         '/static/img/metronomo.jpg'),
    ]
    cur.executemany(
        'INSERT INTO productos (nombre, descripcion, categoria, precio, stock, imagen_url) VALUES (?, ?, ?, ?, ?, ?)',
        productos
    )

    conn.commit()
    conn.close()
    print('[OK] Base de datos inicializada.')
    print(f'   -> {len(usuarios)} usuarios')
    print(f'   -> {len(productos)} productos')

if __name__ == '__main__':
    init_db()
