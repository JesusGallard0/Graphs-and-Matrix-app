import streamlit as st
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import string as sg
import random

COLOR_FONDO = '#00003b'
COLOR_NODO_BASE = '#9fdbe5'
COLOR_ARISTA_BASE = 'red'
COLOR_ARISTA_DESTACADA = '#50fa7b'
COLOR_NODO_INICIO = '#50fa7b'
COLOR_NODO_FIN = '#ff5555'
COLOR_NODO_RUTA = '#f1fa8c'
TAMANO_NODO = 900

PALETA_COLORACION = [
    '#ff5555', '#50fa7b', '#8be9fd', '#f1fa8c', '#bd93f9', '#ffb86c', '#ff79c6',
    '#6272a4', '#00f5d4', '#fee440', '#f15bb5', '#9b5de5', '#00bbf9', '#ff9f1c',
    '#2ec4b6', '#e71d36', '#a8dadc', '#ffcad4', '#b5e48c', '#ffd166'
]


def randmatrix(n):
    while True:
        row = []
        for i in range(n):
            fila = "".join(random.choice("01") for _ in range(n))
            row.append(fila)
        if any("1" in f for f in row):
            return row

def randmatNotRef(n):
    while True:
        row = []
        for i in range(n):
            fila = "".join("0" if j == i else random.choice("01") for j in range(n))
            row.append(fila)
            if any("1" in f for f in row):
                return row

def validar_matriz(texto, n):
    lineas = [l.strip() for l in texto.strip().splitlines() if l.strip()]
    if len(lineas) != n:
        return None, f"La matriz debe tener exactamente {n} filas."
    for i, fila in enumerate(lineas):
        if len(fila) != n or any(c not in ("0", "1") for c in fila):
            return None, f"La fila {i+1} debe tener {n} caracteres y solo 0s y 1s."
    return lineas, None

def format_matrix_text(matrix):
    n = len(matrix)
    strings = sg.ascii_lowercase[:n]
    salida = ["  " + strings, " " + "-" * (n + 2)]
    for i, val in enumerate(matrix):
        salida.append(strings[i] + "|" + val + "|")
    return "\n".join(salida)

def build_peers(matrix, strings):
    peers = []
    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            if val == "1":
                peers.append((strings[i], strings[j]))
    return peers

def numpyconv(matrix):
    newrow = []
    for row in matrix:
        newrow.append([int(c) for c in row])
    return np.array(newrow)




def build_graph(strings, outcome):
    G = nx.DiGraph()
    G.add_nodes_from(strings)
    G.add_edges_from(outcome)

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Grados de salida (Out-degree):**")
        for nodo, grado in G.out_degree():
            st.write(f"- `{nodo}`: {grado}")
    with col2:
        st.write("**Grados de entrada (In-degree):**")
        for nodo, grado in G.in_degree():
            st.write(f"- `{nodo}`: {grado}")

    fig, ax = plt.subplots()
    nx.draw(
        G,
        ax=ax,
        with_labels=True,
        arrows=True,
        node_color=COLOR_NODO_BASE,
        edgecolors="black",
        edge_color=COLOR_ARISTA_BASE,
        font_color="white",
        node_size=TAMANO_NODO,
        width=1,
        arrowsize=25,
    )
    fig.set_facecolor(COLOR_FONDO)
    ax.set_facecolor(COLOR_FONDO)
    st.pyplot(fig)
    plt.close(fig)

def properties(intmatrix):
    diagonal = np.diag(intmatrix)
    reflexive = bool(np.all(diagonal == 1))
    st.write(f"- **Reflexive:** `{reflexive}`")

    n = len(intmatrix)
    simetric = False
    for i in range(n):
        for j in range(n):
            if i != j and intmatrix[i][j] == 1 and intmatrix[j][i] == 1:
                simetric = True
    st.write(f"- **Simetría:** `{'Simetric' if simetric else 'Asimetric'}`")

    transitive = False
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if intmatrix[i][j] == 1 and intmatrix[j][k] == 1 and intmatrix[i][k] == 1:
                    transitive = True
    st.write(f"- **Transitividad:** `{'Transitive' if transitive else 'Non transitive'}`")

    if not reflexive or not transitive:
        rel = "Sin relación"
    elif simetric:
        rel = "Equivalencia"
    else:
        rel = "Orden"
    st.write(f"- **Relación:** `{rel}`")

def buildcolor_graph(strings, outcome):
    G = nx.Graph()
    G.add_nodes_from(strings)
    G.add_edges_from(outcome)

    grados = dict(G.degree())
    nodosO = sorted(strings, key=lambda nodo: (-grados[nodo], nodo))
    st.write("**Orden de nodos:**", nodosO)

    colores = {}
    icolor = 0

    for nodo in nodosO:
        if nodo in colores:
            continue

        color_actual = PALETA_COLORACION[icolor % len(PALETA_COLORACION)]
        colores[nodo] = color_actual
        grupo_actual = [nodo]

        for candidato in nodosO:
            if candidato not in colores:
                puede_pintarse = True
                for miembro in grupo_actual:
                    if G.has_edge(miembro, candidato):
                        puede_pintarse = False
                        break
                if puede_pintarse:
                    colores[candidato] = color_actual
                    grupo_actual.append(candidato)
        icolor += 1

    mapaColores = [colores[nodo] for nodo in G.nodes()]
    st.write(f"**Colores usados:** `{icolor}`")

    fig, ax = plt.subplots()
    nx.draw(
        G,
        ax=ax,
        with_labels=True,
        arrows=False,
        node_color=mapaColores,
        edgecolors="black",
        edge_color=COLOR_ARISTA_BASE,
        font_color="white",
        node_size=TAMANO_NODO,
        width=1,
        arrowsize=25,
    )
    fig.set_facecolor(COLOR_FONDO)
    ax.set_facecolor(COLOR_FONDO)
    st.pyplot(fig)
    plt.close(fig)

def generar_pesos_random(matrix, strings):
    peers = []
    vistos = set()
    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            if val == "1":
                parorden = tuple(sorted((strings[i], strings[j])))
                if parorden not in vistos:
                    vistos.add(parorden)
                    peso = random.randint(1, 10)
                    peers.append((parorden[0], parorden[1], peso))
    return peers

def obtener_aristas_unicas(matrix, strings):
    aristas = []
    vistos = set()
    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            if val == "1":
                parorden = tuple(sorted((strings[i], strings[j])))
                if parorden not in vistos:
                    vistos.add(parorden)
                    aristas.append(parorden)
    return aristas

def build_dijkstra(strings, pesos, inicio, fin):
    G = nx.Graph()
    G.add_nodes_from(strings)
    G.add_weighted_edges_from(pesos)

    nodosorden = sorted(strings)
    distancias = {nodo: float("inf") for nodo in nodosorden}
    distancias[inicio] = 0
    previos = {}
    bloqueados = set()

    lineas_tabla = []
    encabezado = "Actual | " + " | ".join(f"{n:^4}" for n in nodosorden)
    lineas_tabla.append(encabezado)
    lineas_tabla.append("-" * len(encabezado))

    actual = inicio
    while actual is not None:
        bloqueados.add(actual)

        for vecino in G.neighbors(actual):
            if vecino not in bloqueados:
                peso_arista = G[actual][vecino]["weight"]
                nueva_distancia = distancias[actual] + peso_arista
                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    previos[vecino] = actual

        fila_tabla = []
        for n in nodosorden:
            if n in bloqueados and n != actual:
                fila_tabla.append(f"{'X':^4}")
            elif n == actual:
                fila_tabla.append(f"[{distancias[n]}]" if distancias[n] != float("inf") else " .  ")
            elif distancias[n] == float("inf"):
                fila_tabla.append(f"{'.':^4}")
            else:
                fila_tabla.append(f"{distancias[n]:^4}")

        lineas_tabla.append(f"  {actual:^4} | " + " | ".join(fila_tabla))

        if actual == fin:
            break

        candidatos = [n for n in nodosorden if n not in bloqueados and distancias[n] != float("inf")]
        actual = min(candidatos, key=lambda n: distancias[n]) if candidatos else None

    st.write("**Tabla**")
    st.code("\n".join(lineas_tabla))

    ruta = []
    paso = fin
    while paso is not None:
        ruta.insert(0, paso)
        paso = previos.get(paso)

    aristas_ruta = set()
    if distancias[fin] == float("inf"):
        st.warning(f"No hay camino posible de '{inicio}' a '{fin}'.")
    else:
        st.success(f"Ruta más corta: **{' - '.join(ruta)}** | Peso final: **{distancias[fin]}**")
        for i in range(len(ruta) - 1):
            u, v = ruta[i], ruta[i + 1]
            aristas_ruta.add((u, v))
            aristas_ruta.add((v, u))

    pos = nx.spring_layout(G, seed=42)
    colores_nodos = []
    for nodo in G.nodes():
        if nodo == inicio:
            colores_nodos.append(COLOR_NODO_INICIO)
        elif nodo == fin:
            colores_nodos.append(COLOR_NODO_FIN)
        elif nodo in ruta and distancias[fin] != float("inf"):
            colores_nodos.append(COLOR_NODO_RUTA)
        else:
            colores_nodos.append(COLOR_NODO_BASE)

    colores_aristas = [COLOR_ARISTA_DESTACADA if edge in aristas_ruta else "#6272a4" for edge in G.edges()]
    anchos_aristas = [3.5 if edge in aristas_ruta else 1.2 for edge in G.edges()]

    fig, ax = plt.subplots()
    nx.draw(
        G,
        pos,
        ax=ax,
        with_labels=True,
        arrows=False,
        node_color="#9fdbe5",
        edgecolors="black",
        edge_color=colores_aristas,
        font_color="black",
        node_size=TAMANO_NODO,
        width=anchos_aristas,
    )
    #etiquetas_pesos = nx.get_edge_attributes(G, "weight")
    #nx.draw_networkx_edge_labels(
    #    G,
    #    pos,
    #    ax=ax,
    #    edge_labels=etiquetas_pesos,
    #    font_color="#f8f8f2",
    #    font_weight="bold",
    #    bbox={"facecolor": COLOR_FONDO, "edgecolor": "none", "alpha": 0.8},
    #)
    fig.set_facecolor(COLOR_FONDO)
    ax.set_facecolor(COLOR_FONDO)
    st.pyplot(fig)
    plt.close(fig)


def build_base_graph(strings, pesos):
    G = nx.Graph()
    G.add_nodes_from(strings)
    G.add_weighted_edges_from(pesos)

    pos = nx.spring_layout(G, seed=42)
    fig, ax = plt.subplots()
    nx.draw(
        G,
        pos,
        ax=ax,
        with_labels=True,
        arrows=False,
        node_color="#9fdbe5",
        edgecolors="black",
        edge_color="red",
        font_color="black",
        node_size=900,
        width=1.5,
    )

    # Etiquetas de los pesos
    etiquetas_pesos = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(
        G,
        pos,
        ax=ax,
        edge_labels=etiquetas_pesos,
        font_color="#f8f8f2",
        font_weight="bold",
        bbox={"facecolor": "#1e1e2e", "edgecolor": "none", "alpha": 0.8},
    )

    fig.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")
    st.pyplot(fig)
    plt.close(fig)

def build_prim(strings, pesos, inicio):
    G = nx.Graph()
    G.add_nodes_from(strings)
    G.add_weighted_edges_from(pesos)

    visitados = {inicio}
    aristas_mst = []
    costo_total = 0
    pasos = []

    while len(visitados) < len(strings):
        arista_minima = None
        peso_minimo = float("inf")

        for u in visitados:
            for v in G.neighbors(u):
                if v not in visitados and u != v:
                    peso = G[u][v]["weight"]
                    if peso < peso_minimo:
                        peso_minimo = peso
                        arista_minima = (u, v)

        if arista_minima is None:
            st.warning("Aviso: El grafo tiene nodos aislados.")
            break

        u, v = arista_minima
        visitados.add(v)
        aristas_mst.append((u, v))
        costo_total += peso_minimo
        pasos.append(f"Conectando {u} --({peso_minimo})--> {v}")

    st.code("\n".join(pasos) if pasos else "Sin conexiones")
    st.success(f"Costo total: **{costo_total}**")

    pos = nx.spring_layout(G, seed=42)
    fig, ax = plt.subplots()
    nx.draw(
        G,
        pos,
        ax=ax,
        with_labels=True,
        node_color=COLOR_NODO_BASE,
        edgecolors="black",
        edge_color="#555555",
        font_color="black",
        node_size=TAMANO_NODO,
        width=1,
        style="dashed"
    )
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=aristas_mst, edge_color=COLOR_ARISTA_DESTACADA, width=3)
    #etiquetas_pesos = nx.get_edge_attributes(G, 'weight')
    #nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=etiquetas_pesos, font_color="black")
    

    fig.set_facecolor(COLOR_FONDO)
    ax.set_facecolor(COLOR_FONDO)
    ax.set_title("Algoritmo de Prim", color="white")
    st.pyplot(fig)
    plt.close(fig)

def build_kruskal(strings, pesos):
    G = nx.Graph()
    G.add_nodes_from(strings)
    G.add_weighted_edges_from(pesos)

    aristas_ordenadas = sorted(pesos, key=lambda x: x[2])
    padre = {nodo: nodo for nodo in strings}

    def encontrar(nodo):
        while padre[nodo] != nodo:
            padre[nodo] = padre[padre[nodo]]
            nodo = padre[nodo]
        return nodo

    aristas_mst = []
    peso_total = 0
    pasos = []

    for u, v, peso in aristas_ordenadas:
        raiz_u = encontrar(u)
        raiz_v = encontrar(v)
        if raiz_u != raiz_v:
            padre[raiz_u] = raiz_v
            aristas_mst.append((u, v))
            peso_total += peso
            pasos.append(f"Arista validada : ({u} - {v}) con peso {peso}")

    st.code("\n".join(pasos) if pasos else "Sin aristas válidas")
    st.success(f"Peso total mínimo: **{peso_total}**")

    fig, ax = plt.subplots()
    pos = nx.spring_layout(G, seed=42)
    nx.draw(
        G,
        pos,
        ax=ax,
        with_labels=True,
        node_color=COLOR_NODO_BASE,
        edgecolors="black",
        edge_color="#555555",
        font_color="white",
        node_size=TAMANO_NODO,
        width=1,
    )
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=aristas_mst, edge_color=COLOR_ARISTA_DESTACADA, width=3)
    #etiquetas_pesos = nx.get_edge_attributes(G, 'weight')
    #nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=etiquetas_pesos)

    fig.set_facecolor(COLOR_FONDO)
    ax.set_facecolor(COLOR_FONDO)
    st.pyplot(fig)
    plt.close(fig)


st.title("Matrices binarias y Grafos")

#Control 
with st.expander ("Menu",expanded=True):
    st.header("Configuracion")
    modo = st.radio(
        "Elige el modo:",
        ["1. Random", "2. Custom", "3. Color, Dijkstra, Prim, Kruskal"]
    )
    n = st.number_input("Tamano de la matriz nxn :", min_value=2, max_value=26, value=4, step=1)

    submodo = None
    if modo == "3. Color, Dijkstra, Prim, Kruskal":
        submodo = st.radio("Origen de la matriz:", ["Random (no reflexiva)", "Custom"])

    # Entrada manual de matriz si aplica
    texto_matriz = ""
    if modo == "2. Custom" or (modo == "3. Color, Dijkstra, Prim, Kruskal" and submodo == "Custom"):
        ejemplo = "\n".join(["0" * n for _ in range(n)])
        texto_matriz = st.text_area(
            f"Escribe {n} filas de {n} dígitos (0 o 1):",
            value=ejemplo,
            height=150
        )

    if st.button("Generar / Actualizar Matriz", type="primary"):
        if modo == "1. Random":
            st.session_state["matrix"] = randmatrix(n)
            st.session_state.pop("pesos_random", None)
        elif modo == "2. Custom":
            mat, err = validar_matriz(texto_matriz, n)
            if err:
                st.error(err)
            else:
                st.session_state["matrix"] = mat
        elif modo == "3. Color, Dijkstra, Prim, Kruskal":
            if submodo == "Random (no reflexiva)":
                st.session_state["matrix"] = randmatNotRef(n)
                st.session_state.pop("pesos_random", None)
            else:
                mat, err = validar_matriz(texto_matriz, n)
                if err:
                    st.error(err)
                else:
                    temp = numpyconv(mat)
                    if np.any(np.diag(temp) == 1):
                        st.error("No debe tener ningún nodo reflexivo.")
                    else:
                        st.session_state["matrix"] = mat
                        st.session_state.pop("pesos_random", None)

# Ejecución sobre la matriz
matrix = st.session_state.get("matrix")

if matrix is not None:
    intmatrix = numpyconv(matrix)
    n_actual = len(matrix)
    strings = sg.ascii_lowercase[:n_actual]
    outcome = build_peers(matrix, strings)

    col_mat, col_pares = st.columns(2)
    with col_mat:
        st.subheader("Matriz")
        st.code(format_matrix_text(matrix))

    with col_pares:
        st.subheader("Pares ordenados")
        partes = []
        mainrow = None
        for par in outcome:
            if par[0] != mainrow:
                mainrow = par[0]
                partes.append("\n" + f"({par[0]}, {par[1]})")
            else:
                partes.append(f"({par[0]}, {par[1]})")
        finaltxt = ",".join(partes)
        st.code("MxM = {" + finaltxt + "}")

    st.divider()

    if modo == "3. Color, Dijkstra, Prim, Kruskal":
        # Validar que no sea reflexiva
        if np.any(np.diag(intmatrix) == 1):
            st.warning("La matriz tiene nodos reflexivos.")
        else:
            st.subheader("1. Coloracion")
            buildcolor_graph(strings, outcome)

            st.divider()
            st.subheader("2. Configuración de Pesos")
            aristas_unicas = obtener_aristas_unicas(matrix, strings)

            if not aristas_unicas:
                st.info("La matriz no tiene aristas")
            else:
                tipo_pesos = st.radio("Asignación de pesos:", ["Pesos Random", "Pesos Manual"], horizontal=True)
                pesos = []

                if tipo_pesos == "Pesos Random":
                    if "pesos_random" not in st.session_state or st.button("Regenerar pesos random"):
                        st.session_state["pesos_random"] = generar_pesos_random(matrix, strings)
                    pesos = st.session_state["pesos_random"]
                    st.write(", ".join([f"`({u}↔{v}): {w}`" for u, v, w in pesos]))
                else:
                    cols = st.columns(min(4, len(aristas_unicas)))
                    for idx, (u, v) in enumerate(aristas_unicas):
                        with cols[idx % len(cols)]:
                            w = st.number_input(f"Peso ({u} ↔ {v})", min_value=1, value=1, step=1, key=f"peso_{u}_{v}")
                            pesos.append((u, v, int(w)))
                
                st.divider()
                st.subheader("Grafo Original")
                build_base_graph(strings, pesos)

                st.divider()
                st.subheader("3. Dijkstra")
                c1, c2 = st.columns(2)
                inicio_dijk = c1.selectbox("Nodo de entrada:", list(strings), index=0)
                fin_dijk = c2.selectbox("Nodo de salida:", list(strings), index=len(strings) - 1)
                build_dijkstra(strings, pesos, inicio_dijk, fin_dijk)

                st.divider()
                st.subheader("4.Prim")
                inicio_prim = st.selectbox("Nodo inicial para Prim:", list(strings), index=0)
                build_prim(strings, pesos, inicio_prim)

                st.divider()
                st.subheader("5. Kruskal")
                build_kruskal(strings, pesos)

    else:
        st.subheader("Propiedades de la Relación")
        properties(intmatrix)
        st.subheader("Grafo Dirigido")
        build_graph(strings, outcome)
else:
    st.info("Genera o Crea una matriz binaria para aplicar los algoritmos")
