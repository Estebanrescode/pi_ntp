import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

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

# Tema Plotly
px.defaults.template = "plotly_dark"
PALETA = ["#3b82f6", "#10b981", "#f59e0b", "#d946ef", "#4a90e2"]

# ===========================
# 🔗 CARGA DE DATOS DESDE API
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

df_categories    = load_data("categories")
df_products      = load_data("products")
df_users         = load_data("users")
df_pay           = load_data("payMethods")
df_orders        = load_data("orders")
df_order_details = load_data("orderDetails")

# ===========================
# 🛍️ Productos destacados (preámbulo)
# ===========================
st.markdown("## ✨ Algunos de mis productos")
if not (df_products.empty or df_categories.empty):
    df_products = df_products.merge(
        df_categories[["id","name"]],
        how="left",
        left_on="categoriaId",
        right_on="id",
        suffixes=("","_categoria")
    )
    df_products.rename(columns={"name": "categoria"}, inplace=True)

    categorias = sorted(df_products["categoria"].dropna().unique().tolist())
    for cat in categorias:
        st.markdown(f"### 📦 Categoría: **{cat}**")
        df_cat = df_products[df_products["categoria"] == cat].head(2)
        cols = st.columns(len(df_cat))
        for idx, (_, row) in enumerate(df_cat.iterrows()):
            with cols[idx]:
                st.image(row["imagen"], use_container_width=True)
                st.caption(row["nombre"])
else:
    st.markdown("_(No hay productos para mostrar)_")

# ===========================
# 🔧 CÁLCULO DE TOTAL REAL POR ORDEN
# ===========================
if not df_order_details.empty:
    df_order_details["price"]     = pd.to_numeric(df_order_details["price"],    errors="coerce")
    df_order_details["quantity"]  = pd.to_numeric(df_order_details["quantity"], errors="coerce")
    df_order_details["line_total"] = df_order_details["price"] * df_order_details["quantity"]

    df_totals = (
        df_order_details
        .groupby("order_id")["line_total"]
        .sum()
        .reset_index()
        .rename(columns={"line_total":"computed_total"})
    )

    df_orders = df_orders.merge(
        df_totals,
        how="left",
        left_on="id",
        right_on="order_id"
    )

    df_orders["total_amount"] = df_orders["computed_total"].fillna(df_orders["total_amount"])
else:
    st.warning("⚠️ No se encontraron detalles de órdenes (orderDetails). Verifica el endpoint.")

# ===================================
# 📊 Sección — PRODUCTOS
st.header("📊 Dashboard de Productos")
if df_products.empty or df_categories.empty:
    st.warning("⚠️ No hay datos de productos o categorías.")
else:
    df_products["precio"] = pd.to_numeric(df_products["precio"], errors="coerce")
    df_products["stock"]  = pd.to_numeric(df_products["stock"],  errors="coerce")

    tab_prod_graf, tab_prod_tabla = st.tabs(["📈 Gráficas", "📋 Tabla"])
    with tab_prod_graf:
        st.markdown("### 🎛️ Filtros de Productos")
        col1, col2, col3 = st.columns(3)
        with col1:
            categoria_sel = st.selectbox(
                "Selecciona una categoría",
                ["Todas"] + sorted(df_products["categoria"].dropna().unique().tolist()),
                key="filt_prod_categoria"
            )
        with col2:
            stock_estado = st.selectbox(
                "Estado del stock",
                ["Todos", "Disponible (>10)", "Stock bajo (1-10)", "Agotado (0)"],
                key="filt_prod_stock"
            )
        with col3:
            precio_min  = float(df_products["precio"].min())
            precio_max  = float(df_products["precio"].max())
            rango_precio = st.slider(
                "Rango de precios",
                precio_min, precio_max,
                (precio_min, precio_max),
                key="filt_prod_precio"
            )

        df_filtrado_prod = df_products.copy()
        if categoria_sel != "Todas":
            df_filtrado_prod = df_filtrado_prod[df_filtrado_prod["categoria"] == categoria_sel]
        if stock_estado != "Todos":
            if stock_estado == "Disponible (>10)":
                df_filtrado_prod = df_filtrado_prod[df_filtrado_prod["stock"] > 10]
            elif stock_estado == "Stock bajo (1-10)":
                df_filtrado_prod = df_filtrado_prod[(df_filtrado_prod["stock"] > 0) & (df_filtrado_prod["stock"] <= 10)]
            else:
                df_filtrado_prod = df_filtrado_prod[df_filtrado_prod["stock"] == 0]
        df_filtrado_prod = df_filtrado_prod[
            df_filtrado_prod["precio"].between(rango_precio[0], rango_precio[1])
        ]

        # — Nuevo: gráfico de torta para distribución por categoría
        conteo = df_filtrado_prod["categoria"].value_counts().reset_index()
        conteo.columns = ["categoria", "cantidad"]

        fig1 = px.pie(
            conteo,
            names="categoria",
            values="cantidad",
            title="Distribución de productos por categoría",
            color_discrete_sequence=PALETA
        )
        fig1.update_traces(textinfo="label+percent", textposition="inside")
        st.plotly_chart(fig1, use_container_width=True)

        # — También mantenemos gráfico de barras para precio promedio
        precio_prom = df_filtrado_prod.groupby("categoria")["precio"].mean().reset_index()
        fig2 = px.bar(
            precio_prom,
            x="categoria",
            y="precio",
            color="precio",
            color_continuous_scale=PALETA,
            title="Precio promedio por categoría",
            text=precio_prom["precio"].round(2)
        )
        fig2.update_traces(texttemplate="%{text:,.2f}", textposition="outside")
        fig2.update_layout(xaxis_tickangle=-15)
        st.plotly_chart(fig2, use_container_width=True)

    with tab_prod_tabla:
        st.markdown("#### Detalle de productos filtrados")
        st.dataframe(
            df_filtrado_prod[["id","nombre","precio","stock","categoria"]],
            use_container_width=True
        )

# ===================================
# 📦 Sección — PEDIDOS
st.header("📦 Dashboard de Pedidos")
if df_orders.empty:
    st.warning("⚠️ No hay datos suficientes para mostrar los pedidos.")
else:
    df_orders["total_amount"] = pd.to_numeric(df_orders["total_amount"], errors="coerce")
    df_orders["status"]       = df_orders["status"].astype(str)
    df_orders["created_at"]   = pd.to_datetime(df_orders["created_at"], errors="coerce")

    if not df_users.empty:
        df_orders = df_orders.merge(
            df_users[["id","fullname"]],
            how="left",
            left_on="user_id",
            right_on="id",
            suffixes=("","_user")
        )
        df_orders.rename(columns={"fullname":"usuario"}, inplace=True)
    else:
        df_orders["usuario"] = "Desconocido"

    if not df_pay.empty:
        df_orders = df_orders.merge(
            df_pay[["id","name"]],
            how="left",
            left_on="payment_method_id",
            right_on="id",
            suffixes=("","_pay")
        )
        df_orders.rename(columns={"name":"metodo_pago"}, inplace=True)
    else:
        df_orders["metodo_pago"] = "No especificado"

    tab_ord_graf, tab_ord_tabla = st.tabs(["📈 Gráficas", "📋 Tabla"])
    with tab_ord_graf:
        st.markdown("### 🎛️ Filtros de Pedidos")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            usuarios = ["Todos"] + sorted(df_orders["usuario"].dropna().unique().tolist())
            usuario_sel = st.selectbox(
                "👤 Usuario",
                usuarios,
                key="filt_ord_usuario"
            )
        with col2:
            metodos = ["Todos"] + sorted(df_orders["metodo_pago"].dropna().unique().tolist())
            metodo_sel = st.selectbox(
                "💳 Método de pago",
                metodos,
                key="filt_ord_metodo"
            )
        with col3:
            estados = ["Todos"] + sorted(df_orders["status"].dropna().unique().tolist())
            estado_sel = st.selectbox(
                "📦 Estado del pedido",
                estados,
                key="filt_ord_estado"
            )
        with col4:
            fecha_min = df_orders["created_at"].min().date()
            fecha_max = df_orders["created_at"].max().date()
            rango_fecha = st.date_input("📅 Rango de fechas", [fecha_min, fecha_max], key="filt_ord_fechas")

        # Aplicación de filtros
        df_filtrado_ord = df_orders.copy()
        if usuario_sel != "Todos":
            df_filtrado_ord = df_filtrado_ord[df_filtrado_ord["usuario"] == usuario_sel]
        if metodo_sel != "Todos":
            df_filtrado_ord = df_filtrado_ord[df_filtrado_ord["metodo_pago"] == metodo_sel]
        if estado_sel != "Todos":
            df_filtrado_ord = df_filtrado_ord[df_filtrado_ord["status"] == estado_sel]
        df_filtrado_ord = df_filtrado_ord[
            (df_filtrado_ord["created_at"].dt.date >= rango_fecha[0]) &
            (df_filtrado_ord["created_at"].dt.date <= rango_fecha[1])
        ]

        st.metric(label="🧮 Total de órdenes", value=f"{len(df_filtrado_ord)}")
        st.metric(label="💰 Ventas totales", value=f"${df_filtrado_ord['total_amount'].sum():,.2f}")
        st.metric(label="📊 Promedio por orden", value=f"${df_filtrado_ord['total_amount'].mean():,.2f}")

        top_5 = df_filtrado_ord.groupby("usuario")["total_amount"].sum().nlargest(5).reset_index()
        fig_top = px.bar(
            top_5,
            x="usuario",
            y="total_amount",
            color="total_amount",
            color_continuous_scale=PALETA,
            title="Top 5 usuarios con mayores ventas",
            text=top_5["total_amount"]
        )
        fig_top.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_top.update_layout(xaxis_tickangle=-15)
        st.plotly_chart(fig_top, use_container_width=True)

    with tab_ord_tabla:
        st.markdown("#### Detalle de pedidos filtrados")
        st.dataframe(
            df_filtrado_ord[["id","usuario","metodo_pago","status","total_amount","created_at"]],
            use_container_width=True
        )

# ===================================
# 📆 Sección — VENTAS POR AÑO
st.header("📆 Ventas por Año")
if not df_orders.empty:
    df_v = df_orders.copy()
    df_v["year"] = df_v["created_at"].dt.year

    tab_year_graf, tab_year_tabla = st.tabs(["📈 Gráficas", "📋 Tabla"])
    with tab_year_graf:
        st.markdown("### 🎛️ Filtro de años")
        anio_min   = int(df_v["year"].min())
        anio_max   = int(df_v["year"].max())
        rango_anios = st.slider(
            "Selecciona año o rango de años",
            anio_min, anio_max,
            (anio_min, anio_max),
            key="filt_year_range"
        )

        df_vf = df_v[(df_v["year"] >= rango_anios[0]) & (df_v["year"] <= rango_anios[1])]
        ventas_por_anio = df_vf.groupby("year")["total_amount"].sum().reset_index()

        fig_year = px.bar(
            ventas_por_anio,
            x="year",
            y="total_amount",
            color="total_amount",
            color_continuous_scale=PALETA,
            title="Ventas Totales por Año",
            text=ventas_por_anio["total_amount"]
        )
        fig_year.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_year.update_layout(xaxis_title="Año", yaxis_title="Ventas Totales", xaxis_tickangle=-45)
        st.plotly_chart(fig_year, use_container_width=True)

    with tab_year_tabla:
        st.markdown("### 📋 Tabla resumen de ventas por año")
        st.dataframe(ventas_por_anio, use_container_width=True)
else:
    st.warning("⚠️ No hay datos suficientes para calcular ventas por año.")

# ===================================
# 🏆 Sección — TOP 10 Productos más vendidos (todos los registros)
st.header("🏆 Top 10 Productos más Vendidos")

if not (df_order_details.empty or df_products.empty or df_orders.empty):
    df_od = df_order_details.copy()
    df_od["quantity"] = pd.to_numeric(df_od["quantity"], errors="coerce")

    df_prod2 = df_products.copy()
    df_prod2 = df_prod2.rename(columns={"id":"product_id", "nombre":"nombre_producto"})

    df_od3 = df_od.merge(
        df_prod2[["product_id","nombre_producto"]],
        how="left",
        left_on="product_id",
        right_on="product_id"
    )

    ventas_prod = (
        df_od3
        .groupby(["product_id","nombre_producto"])["quantity"]
        .sum()
        .reset_index()
        .rename(columns={"quantity":"cantidad_vendida"})
    )

    df_top10 = ventas_prod.sort_values("cantidad_vendida", ascending=False).head(10).reset_index(drop=True)

    tab_prod_top_graf, tab_prod_top_tabla = st.tabs(["📈 Gráfica", "📋 Tabla"])
    with tab_prod_top_graf:
        fig_top10 = px.bar(
            df_top10,
            x="nombre_producto",
            y="cantidad_vendida",
            color="cantidad_vendida",
            color_continuous_scale=PALETA,
            title="Top 10 Productos más Vendidos (registro completo)",
            text=df_top10["cantidad_vendida"]
        )
        fig_top10.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_top10.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_top10, use_container_width=True)

    with tab_prod_top_tabla:
        st.markdown("#### 📋 Tabla Top 10 Productos")
        st.dataframe(df_top10, use_container_width=True)
else:
    st.warning("⚠️ No hay datos suficientes para calcular el Top 10 de productos.")

# ===================================
# 🌟 Sección — TOP 5 Usuarios (ventas totales)
st.header("🌟 Top 5 Usuarios por Ventas Totales")

if not (df_orders.empty or df_users.empty):
    df_o2 = df_orders.copy()
    df_o2["total_amount"] = pd.to_numeric(df_o2["total_amount"], errors="coerce")

    top_users = (
        df_o2
        .groupby("usuario")["total_amount"]
        .sum()
        .reset_index()
        .rename(columns={"total_amount":"venta_total_usuario"})
    )

    df_top5u = top_users.sort_values("venta_total_usuario", ascending=False).head(5).reset_index(drop=True)

    tab_user_top_graf, tab_user_top_tabla = st.tabs(["📈 Gráfica", "📋 Tabla"])
    with tab_user_top_graf:
        fig_top5u = px.bar(
            df_top5u,
            x="usuario",
            y="venta_total_usuario",
            color="venta_total_usuario",
            color_continuous_scale=PALETA,
            title="Top 5 Usuarios (ventas totales)",
            text=df_top5u["venta_total_usuario"]
        )
        fig_top5u.update_traces(texttemplate="%{text:,.2f}", textposition="outside")
        fig_top5u.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_top5u, use_container_width=True)

    with tab_user_top_tabla:
        st.markdown("#### 📋 Tabla Top 5 Usuarios")
        st.dataframe(df_top5u, use_container_width=True)
else:
    st.warning("⚠️ No hay datos suficientes para calcular el Top 5 de usuarios.")
