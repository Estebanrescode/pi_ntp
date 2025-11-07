import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# ===========================
# 🎨 CONFIGURACIÓN DE PÁGINA
# ===========================
st.set_page_config(
    page_title="Dashboard Neonix",
    layout="wide",
    page_icon="🧢"
)

st.title("🧢 Dashboard Neonix — E-commerce de Ropa Urbana")
st.markdown("Explora tus datos de clientes, productos y pedidos de forma interactiva.")

# ===========================
# 🔗 CARGA DE DATOS DESDE MOCKOON
# ===========================
BASE_URL = "http://localhost:3000/api"

def load_data(endpoint):
    try:
        url = f"{BASE_URL}/{endpoint}"
        response = requests.get(url)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception as e:
        st.error(f"❌ Error al cargar datos desde {url}: {e}")
        return pd.DataFrame()

df_categories = load_data("categories")
df_products = load_data("products")
df_users = load_data("users")
df_pay = load_data("payMethods")
df_orders = load_data("orders")

# ===========================
# 🧩 TAB MENU PRINCIPAL
# ===========================
tabs = st.tabs(["📊 Productos", "📦 Pedidos"])

# =======================================================
# 📊 TAB 1 — PRODUCTOS
# =======================================================
with tabs[0]:
    st.header("📊 Dashboard de Productos")

    if df_products.empty or df_categories.empty:
        st.warning("⚠️ No hay datos de productos o categorías.")
    else:
        # Convertir numéricos
        df_products["precio"] = pd.to_numeric(df_products["precio"], errors="coerce")
        df_products["stock"] = pd.to_numeric(df_products["stock"], errors="coerce")

        # Unir categorías
        df_products = df_products.merge(
            df_categories[["id", "name"]],
            how="left",
            left_on="categoriaId",
            right_on="id",
            suffixes=("", "_categoria")
        )
        df_products.rename(columns={"name": "categoria"}, inplace=True)

        # Filtros
        st.markdown("### 🎛️ Filtros de Productos")
        col1, col2 = st.columns(2)

        with col1:
            categoria_sel = st.selectbox(
                "Selecciona una categoría",
                ["Todas"] + sorted(df_products["categoria"].dropna().unique().tolist())
            )

        with col2:
            precio_min = float(df_products["precio"].min())
            precio_max = float(df_products["precio"].max())
            rango_precio = st.slider("Rango de precios", precio_min, precio_max, (precio_min, precio_max))

        # Aplicar filtros
        df_filtrado = df_products.copy()
        if categoria_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado["categoria"] == categoria_sel]
        df_filtrado = df_filtrado[df_filtrado["precio"].between(rango_precio[0], rango_precio[1])]

        # Gráficos
        st.markdown("#### 📦 Cantidad de productos por categoría")
        conteo = df_filtrado["categoria"].value_counts()
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        ax1.bar(conteo.index, conteo.values, color="#3b82f6")
        ax1.set_title("Productos por categoría")
        plt.xticks(rotation=15)
        st.pyplot(fig1, use_container_width=True)

        st.markdown("#### 💰 Precio promedio por categoría")
        precio_promedio = df_filtrado.groupby("categoria")["precio"].mean().reset_index()
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ax2.bar(precio_promedio["categoria"], precio_promedio["precio"], color="#10b981")
        ax2.set_title("Precio promedio por categoría")
        plt.xticks(rotation=15)
        st.pyplot(fig2, use_container_width=True)

        # Tabla
        st.markdown("### 📋 Detalle de productos filtrados")
        st.dataframe(df_filtrado[["id", "nombre", "precio", "stock", "categoria"]], use_container_width=True)

# =======================================================
# 📦 TAB 2 — PEDIDOS
# =======================================================
with tabs[1]:
    st.header("📦 Dashboard de Pedidos")

    if df_orders.empty:
        st.warning("⚠️ No hay datos suficientes para mostrar los pedidos.")
    else:
        opcion = st.radio(
            "Selecciona una vista:",
            ["1️⃣ Detalle de Pedidos", "2️⃣ Análisis de Ventas"],
            horizontal=True
        )

        df_orders["total_amount"] = pd.to_numeric(df_orders["total_amount"], errors="coerce")
        df_orders["status"] = df_orders["status"].astype(str)

        if not df_users.empty:
            df_orders = df_orders.merge(
                df_users[["id", "fullname"]],
                how="left",
                left_on="user_id",
                right_on="id",
                suffixes=("", "_user")
            )
            df_orders.rename(columns={"fullname": "usuario"}, inplace=True)
        else:
            df_orders["usuario"] = "Desconocido"

        if not df_pay.empty:
            df_orders = df_orders.merge(
                df_pay[["id", "name"]],
                how="left",
                left_on="payment_method_id",
                right_on="id",
                suffixes=("", "_pay")
            )
            df_orders.rename(columns={"name": "metodo_pago"}, inplace=True)
        else:
            df_orders["metodo_pago"] = "No especificado"

        # OPCIÓN 1️⃣ — DETALLE DE PEDIDOS
        if opcion == "1️⃣ Detalle de Pedidos":
            st.markdown("### 🎛️ Filtros de búsqueda de pedidos")
            col1, col2, col3 = st.columns(3)

            with col1:
                usuarios = ["Todos"] + sorted(df_orders["usuario"].dropna().unique().tolist())
                usuario_sel = st.selectbox("👤 Usuario", usuarios)

            with col2:
                metodos = ["Todos"] + sorted(df_orders["metodo_pago"].dropna().unique().tolist())
                metodo_sel = st.selectbox("💳 Método de pago", metodos)

            with col3:
                total_min = float(df_orders["total_amount"].min())
                total_max = float(df_orders["total_amount"].max())
                rango_total = st.slider("💰 Rango de montos", total_min, total_max, (total_min, total_max))

            col4, col5 = st.columns(2)
            with col4:
                solo_entregados = st.checkbox("✅ Solo pedidos entregados", value=False)
            with col5:
                ordenar_por = st.radio("↕️ Ordenar por", ["Total", "Usuario"], horizontal=True)

            df_filtrado = df_orders.copy()
            if usuario_sel != "Todos":
                df_filtrado = df_filtrado[df_filtrado["usuario"] == usuario_sel]
            if metodo_sel != "Todos":
                df_filtrado = df_filtrado[df_filtrado["metodo_pago"] == metodo_sel]
            df_filtrado = df_filtrado[df_filtrado["total_amount"].between(rango_total[0], rango_total[1])]
            if solo_entregados:
                df_filtrado = df_filtrado[df_filtrado["status"].str.lower().str.contains("delivered")]

            df_filtrado = df_filtrado.sort_values(by="total_amount" if ordenar_por == "Total" else "usuario")

            if not df_filtrado.empty:
                st.markdown("## 🏆 Top 5 Mejores Compradores")

                # 🔹 Mostrar solo los 5 mejores compradores
                top_5 = (
                    df_filtrado.groupby("usuario")["total_amount"]
                    .sum()
                    .nlargest(5)
                    .reset_index()
                )

                fig_top, ax_top = plt.subplots(figsize=(7, 4))
                bars = ax_top.bar(top_5["usuario"], top_5["total_amount"], color="#10b981")
                ax_top.bar_label(bars, labels=[f"${v:,.0f}" for v in top_5["total_amount"]], label_type="edge")
                ax_top.set_title("Top 5 usuarios con mayores ventas")
                plt.xticks(rotation=15, ha="right")
                st.pyplot(fig_top, use_container_width=True)

                st.markdown("## 📋 Detalle de pedidos filtrados")
                st.dataframe(
                    df_filtrado[["id", "usuario", "metodo_pago", "status", "total_amount"]],
                    use_container_width=True
                )
            else:
                st.warning("⚠️ No hay pedidos que cumplan los filtros seleccionados.")

        # OPCIÓN 2️⃣ — ANÁLISIS DE VENTAS
        elif opcion == "2️⃣ Análisis de Ventas":
            st.markdown("## 📈 Análisis de Ventas Totales")

            if "created_at" in df_orders.columns:
                df_orders["created_at"] = pd.to_datetime(df_orders["created_at"], errors="coerce")
                df_orders["mes"] = df_orders["created_at"].dt.to_period("M").astype(str)

                # 🔹 Filtro temporal
                fechas = df_orders["created_at"].dropna()
                fecha_min, fecha_max = fechas.min(), fechas.max()
                rango_fecha = st.slider(
                    "📅 Selecciona el rango de tiempo",
                    min_value=fecha_min.to_pydatetime(),
                    max_value=fecha_max.to_pydatetime(),
                    value=(fecha_min.to_pydatetime(), fecha_max.to_pydatetime()),
                    format="DD/MM/YYYY"
                )

                df_filtrado = df_orders[
                    (df_orders["created_at"] >= rango_fecha[0]) &
                    (df_orders["created_at"] <= rango_fecha[1])
                ]

                ventas_mensuales = df_filtrado.groupby("mes")["total_amount"].sum().reset_index()
                ticket_promedio = df_filtrado.groupby("mes")["total_amount"].mean().reset_index()

                fig1, ax1 = plt.subplots(figsize=(10, 5))
                ax1.plot(ventas_mensuales["mes"], ventas_mensuales["total_amount"],
                         marker="o", color="#3b82f6", linewidth=2)
                ax1.set_title("Tendencia de Ventas Totales por Mes", fontsize=13, pad=10)
                plt.xticks(rotation=45, ha="right")
                st.pyplot(fig1, use_container_width=True)

                fig2, ax2 = plt.subplots(figsize=(10, 5))
                bars = ax2.bar(ticket_promedio["mes"], ticket_promedio["total_amount"], color="#f59e0b", alpha=0.85)
                ax2.bar_label(bars, labels=[f"${v:,.0f}" for v in ticket_promedio["total_amount"]], label_type="edge")
                ax2.set_title("Ticket Promedio por Mes", fontsize=13, pad=10)
                plt.xticks(rotation=45, ha="right")
                st.pyplot(fig2, use_container_width=True)

                resumen = ventas_mensuales.merge(ticket_promedio, on="mes", suffixes=("_total", "_promedio"))
                resumen.rename(columns={
                    "mes": "Mes",
                    "total_amount_total": "Ventas Totales ($)",
                    "total_amount_promedio": "Ticket Promedio ($)"
                }, inplace=True)
                st.markdown("### 📋 Resumen Mensual")
                st.dataframe(resumen, use_container_width=True)
            else:
                st.warning("⚠️ No hay columna 'created_at' para calcular las ventas mensuales.")
