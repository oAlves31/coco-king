import streamlit as st
from datetime import date

# --- Dados iniciais ---
sabores = {
    "Coco King": ["Água de coco", "Melância", "Maracujá", "Morango", "Maçã verde", "Laranja", "Cereja", "Sal e Limão"],
    "Ice Badas": ["Água de coco", "Melância", "Maracujá", "Morango", "Maçã verde"]
}

icones_sabores = {
    "Água de coco": "🥥",
    "Melância": "🍉",
    "Maracujá": "🥭",
    "Morango": "🍓",
    "Maçã verde": "🍏",
    "Laranja": "🍊",
    "Cereja": "🍒",
    "Sal e Limão": "🍺"
}

if "estoque" not in st.session_state:
    st.session_state.estoque = {}

if "sacola" not in st.session_state:
    st.session_state.sacola = []

if "reservas" not in st.session_state:
    st.session_state.reservas = []

# --- Interface com abas ---
st.sidebar.image("logo.png", width=400)

st.sidebar.title("Menu")

# Contador de reservas no menu
num_reservas = len(st.session_state.reservas)
reserva_label = f"Reservas ({num_reservas})" if num_reservas else "Reservas"

pagina = st.sidebar.radio("Navegar para:", ["Entrada de Estoque", reserva_label, "Pedidos Feitos"])

st.sidebar.markdown(
    "<hr style='margin-top:30px; margin-bottom:5px;'>"
    "<p style='text-align: center; font-size: 12px; color: gray;'>Created by Eric Souza</p>",
    unsafe_allow_html=True
)


# --- Página de Estoque ---
if pagina == "Entrada de Estoque":
    st.title("🧊 Controle de Estoque - Coco King")
    st.header("➕ Entrada de Estoque")

    with st.form("form_estoque"):
        marca = st.selectbox("Marca", list(sabores.keys()))
        sabor = st.selectbox("Sabor", sabores[marca])
        quantidade = st.number_input("Quantidade produzida", min_value=1, step=1)
        submitted = st.form_submit_button("Adicionar ao estoque")

        if submitted:
            chave = (marca, sabor)
            if chave in st.session_state.estoque:
                st.session_state.estoque[chave] += quantidade
            else:
                st.session_state.estoque[chave] = quantidade
            st.success(f"{quantidade} unidades de {sabor} ({marca}) adicionadas ao estoque!")

    st.header("📦 Estoque Atual")

    if st.session_state.estoque:
        estoque_coco_king = []
        estoque_ice_badas = []

        for (marca, sabor), qtd in st.session_state.estoque.items():
            nome_com_icone = f"{icones_sabores.get(sabor, '')} {sabor}"
            item = {"Sabor": nome_com_icone, "Quantidade": qtd}
            if marca == "Coco King":
                estoque_coco_king.append(item)
            elif marca == "Ice Badas":
                estoque_ice_badas.append(item)

        if estoque_coco_king:
            st.subheader("🥥 Coco King")
            st.dataframe(estoque_coco_king, use_container_width=True)

        if estoque_ice_badas:
            st.subheader("❄️ Ice Badas")
            st.dataframe(estoque_ice_badas, use_container_width=True)
    else:
        st.info("Nenhum item em estoque ainda.")

# --- Página de Reservas ---
elif "Reservas" in pagina:
    st.title("📦 Fazer Reserva de Pedido")

    st.subheader("1. Adicione itens à sacola")

    with st.form("form_sacola"):
        marca = st.selectbox("Marca", list(sabores.keys()), key="sacola_marca")
        sabor = st.selectbox("Sabor", sabores[marca], key="sacola_sabor")
        quantidade = st.number_input("Quantidade desejada", min_value=1, step=1, key="sacola_qtd")
        adicionar = st.form_submit_button("Adicionar à sacola")

        if adicionar:
            st.session_state.sacola.append({
                "marca": marca,
                "sabor": sabor,
                "quantidade": quantidade
            })
            st.success(f"{quantidade} unidades de {sabor} ({marca}) adicionadas à sacola.")

    if st.session_state.sacola:
        st.subheader("🛒 Itens na sacola")
        for i, item in enumerate(st.session_state.sacola):
            st.write(f"{i+1}. {item['quantidade']}x {icones_sabores.get(item['sabor'], '')} {item['sabor']} ({item['marca']})")

        st.subheader("2. Finalizar pedido")
        cliente = st.text_input("Nome do Cliente")
        data_entrega = st.date_input("Data da entrega", value=date.today())
        finalizar = st.button("📤 Finalizar Pedido")

        if finalizar:
            if not cliente:
                st.warning("Digite o nome do cliente.")
            else:
                # Finaliza mesmo sem estoque
                st.session_state.reservas.append({
                    "cliente": cliente,
                    "data": data_entrega,
                    "itens": [
                        {
                            "marca": item["marca"],
                            "sabor": item["sabor"],
                            "quantidade": item["quantidade"],
                            "estoque_momento_pedido": st.session_state.estoque.get((item["marca"], item["sabor"]), 0)
                        }
                        for item in st.session_state.sacola
                    ],
                    "entregue": False
                })


                # Diminui estoque APENAS se tiver quantidade suficiente
                for item in st.session_state.sacola:
                    chave = (item["marca"], item["sabor"])
                    if chave in st.session_state.estoque:
                        if st.session_state.estoque[chave] >= item["quantidade"]:
                            st.session_state.estoque[chave] -= item["quantidade"]
                        else:
                            # Estoque insuficiente, não desconta
                            pass

                st.success("✅ Pedido registrado, mesmo com estoque insuficiente.")
                st.session_state.sacola.clear()

# --- Página de Pedidos Feitos ---
elif pagina == "Pedidos Feitos":
    st.title("📋 Pedidos Realizados")

    if not st.session_state.reservas:
        st.info("Nenhum pedido realizado ainda.")
    else:
        for i, pedido in enumerate(st.session_state.reservas):
            entregue_key = f"entregue_{i}"
            st.markdown(f"### Pedido {i+1} - {pedido['cliente']} - {pedido.get('data', date.today()).strftime('%d/%m/%Y')}")

            entregue = st.checkbox("✅ Pedido Entregue", value=pedido.get("entregue", False), key=entregue_key)
            st.session_state.reservas[i]["entregue"] = entregue

            for item in pedido["itens"]:
                st.write(f"🔹 {item['quantidade']}x {icones_sabores.get(item['sabor'], '')} {item['sabor']} ({item['marca']})")


            if entregue:
                st.success("Este pedido foi marcado como entregue.")
            else:
                st.info("Este pedido ainda não foi entregue.")

    