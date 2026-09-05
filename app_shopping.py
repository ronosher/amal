import json
import os
import streamlit as st

# הגדרת תצוגה מותאמת לטלפון נייד
st.set_page_config(
    page_title="קניות משפחת דבשה",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# קובצי נתונים
CATALOG_FILE = "products_catalog.json"
CART_FILE = "shopping_cart.json"

# קטלוג ברירת מחדל התחלתי (אם אין קובץ שמור)
DEFAULT_CATALOG = {
    "🥑 ירקות ופירות": [
        "עגבניות",
        "מלפפונים",
        "בצל",
        "תפוחי אדמה",
        "גזר",
        "פלפל אדום",
        "חסה",
        "תפוחים",
        "בננות",
        "לימון",
    ],
    "🥛 מוצרי חלב וביצים": [
        "חלב 3%",
        "ביצים L",
        "גבינה צהובה",
        "קוטג'",
        "חמאה",
        "יוגורט",
        "גבינה לבנה",
        "שמנת חמוצה",
    ],
    "🥩 בשרים ודגים": [
        "חזה עוף",
        "בשר טחון",
        "כרעיים",
        "סטייק פרגית",
        "סלמון קפוא",
        "נקניקיות",
    ],
    "❄️ קפואים": [
        "פיצה קפואה",
        "צ'יפס",
        "ירקות קפואים (סנפרוסט)",
        "מלאווח",
        "גלידה",
    ],
    "🥫 יבשים ומזווה": [
        "אורז",
        "פסטה",
        "שמן זית",
        "שמן קנולה",
        "רסק עגבניות",
        "טונה בקופסה",
        "פתיתים",
        "סוכר",
        "מלח",
        "קפה",
    ],
    "🥖 מאפים": ["לחם פרוס", "פיתות", "לחמניות", "חלה"],
    "🧻 ניקיון ופארם": [
        "נייר טואלט",
        "נייר סופג",
        "נוזל כלים",
        "סבון ידיים",
        "שמפו",
        "אבקת כביסה",
        "מרכך כביסה",
        "שקיות אשפה",
    ],
}


# טעינת קטלוג המוצרים
def load_catalog():
    if os.path.exists(CATALOG_FILE):
        try:
            with open(CATALOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_CATALOG


# שמירת קטלוג המוצרים
def save_catalog(catalog_data):
    with open(CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, ensure_ascii=False, indent=4)


# טעינת מצב הסל
def load_cart_state():
    if os.path.exists(CART_FILE):
        try:
            with open(CART_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


# שמירת מצב הסל
def save_cart_state(cart_data):
    with open(CART_FILE, "w", encoding="utf-8") as f:
        json.dump(cart_data, f, ensure_ascii=False, indent=4)


# אתחול Session State
if "catalog" not in st.session_state:
    st.session_state.catalog = load_catalog()

if "cart" not in st.session_state:
    st.session_state.cart = load_cart_state()

catalog = st.session_state.catalog

# כותרת ראשית ומעוצבת
st.markdown(
    """
    <div style='text-align: center; background-color: #0f172a; padding: 15px; border-radius: 12px; color: white; margin-bottom: 20px;'>
        <h2 style='color: #facc15; margin:0;'>🛒 קניות משפחת דבשה</h2>
        <p style='margin: 5px 0 0 0; font-size: 14px; color: #cbd5e1;'>רשימת קניות משותפת בזמן אמת</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 3 הטאבים הראשיים
tab1, tab2, tab3 = st.tabs(["📋 רשימת מצרכים", "🛒 סל קניות", "⚙️ ניהול מוצרים"])

# ---------------------------------------------------------
# טאב 1: רשימת מצרכים (בחירה והוספה לסל)
# ---------------------------------------------------------
with tab1:
    st.caption("בחר קטגוריה או חפש מוצר כדי להוסיף לסל:")

    categories = ["כל המצרכים"] + list(catalog.keys())
    selected_cat = st.selectbox("סינון לפי קטגוריה:", categories, key="t1_cat")

    search_query = st.text_input("🔍 חיפוש מהיר של מוצר:", "", key="t1_search").strip()

    items_to_show = []
    if selected_cat == "כל המצרכים":
        all_items = []
        for cat, items in catalog.items():
            for item in items:
                all_items.append((item, cat))
        items_to_show = sorted(all_items, key=lambda x: x[0])
    else:
        items_to_show = [(item, selected_cat) for item in catalog.get(selected_cat, [])]

    if search_query:
        items_to_show = [
            (item, cat)
            for item, cat in items_to_show
            if search_query.lower() in item.lower()
        ]

    st.markdown("---")

    if not items_to_show:
        st.info("לא נמצאו מוצרים תואמים.")
    else:
        for item, cat in items_to_show:
            col_name, col_controls = st.columns([2, 1.5])

            col_name.markdown(
                f"**{item}**<br><small style='color:gray;'>{cat}</small>",
                unsafe_allow_html=True,
            )

            current_qty = st.session_state.cart.get(item, {}).get("qty", 0)

            c_minus, c_qty, c_plus = col_controls.columns([1, 1, 1])

            if c_minus.button("➖", key=f"dec_{item}"):
                if current_qty > 1:
                    st.session_state.cart[item]["qty"] -= 1
                elif current_qty == 1:
                    del st.session_state.cart[item]
                save_cart_state(st.session_state.cart)
                st.rerun()

            c_qty.markdown(
                f"<h4 style='text-align: center; margin: 0;'>{current_qty}</h4>",
                unsafe_allow_html=True,
            )

            if c_plus.button("➕", key=f"inc_{item}"):
                if item not in st.session_state.cart:
                    st.session_state.cart[item] = {
                        "qty": 1,
                        "category": cat,
                        "checked": False,
                    }
                else:
                    st.session_state.cart[item]["qty"] += 1
                save_cart_state(st.session_state.cart)
                st.rerun()

            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)


# ---------------------------------------------------------
# טאב 2: סל קניות (עבודה בסופרמרקט)
# ---------------------------------------------------------
with tab2:
    cart_items = st.session_state.cart

    if not cart_items:
        st.success("🎉 סל הקניות ריק! הוסף מוצרים מטאב 'רשימת מצרכים'.")
    else:
        cart_categories = ["כל המצרכים"] + sorted(
            list(set(info["category"] for info in cart_items.values()))
        )
        cart_cat_filter = st.selectbox(
            "תצוגת סל לפי קטגוריה:", cart_categories, key="t2_cat"
        )

        if st.button("🗑️ נקה את כל הסל לקנייה חדשה", use_container_width=True):
            st.session_state.cart = {}
            save_cart_state({})
            st.rerun()

        st.markdown("---")

        pending_items = []
        collected_items = []

        for item, info in cart_items.items():
            if (
                cart_cat_filter != "כל המצרכים"
                and info["category"] != cart_cat_filter
            ):
                continue
            if info.get("checked", False):
                collected_items.append((item, info))
            else:
                pending_items.append((item, info))

        st.subheader(f"🛒 לקחת מהמדף ({len(pending_items)})")

        if not pending_items and collected_items:
            st.balloons()
            st.success("👏 סיימתם את כל הקניות בסל!")

        for item, info in pending_items:
            col_chk, col_txt, col_qty = st.columns([0.8, 2, 1])

            checked = col_chk.checkbox("", value=False, key=f"chk_{item}")
            if checked:
                st.session_state.cart[item]["checked"] = True
                save_cart_state(st.session_state.cart)
                st.rerun()

            col_txt.markdown(
                f"**{item}**<br><small style='color:gray;'>{info['category']}</small>",
                unsafe_allow_html=True,
            )
            col_qty.markdown(
                f"<b>כמות: {info['qty']}</b>", unsafe_allow_html=True
            )
            st.markdown("<hr style='margin: 4px 0;'>", unsafe_allow_html=True)

        if collected_items:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander(
                f"✅ מוצרים שכבר בעגלה ({len(collected_items)})"
            ):
                for item, info in collected_items:
                    col_chk, col_txt = st.columns([0.8, 3])
                    uncheck = col_chk.checkbox(
                        "", value=True, key=f"unchk_{item}"
                    )
                    if not uncheck:
                        st.session_state.cart[item]["checked"] = False
                        save_cart_state(st.session_state.cart)
                        st.rerun()

                    col_txt.markdown(
                        f"~~{item}~~ (כמות: {info['qty']})",
                        unsafe_allow_html=True,
                    )


# ---------------------------------------------------------
# טאב 3: ניהול מוצרים וקטגוריות (הוספה חדשה מהטלפון)
# ---------------------------------------------------------
with tab3:
    st.subheader("➕ הוספת מוצר חדש לקטלוג")
    with st.form("add_product_form"):
        new_product_name = st.text_input("שם המוצר החדש:").strip()
        target_category = st.selectbox("בחר קטגוריה:", list(catalog.keys()))
        submit_product = st.form_submit_button(
            "שמור מוצר בקטלוג", use_container_width=True
        )

        if submit_product:
            if not new_product_name:
                st.error("נא להזין שם מוצר.")
            elif new_product_name in [
                item for items in catalog.values() for item in items
            ]:
                st.warning("המוצר כבר קיים בקטלוג!")
            else:
                catalog[target_category].append(new_product_name)
                # מיון הקטגוריה מחדש לפי א-ב
                catalog[target_category] = sorted(catalog[target_category])
                save_catalog(catalog)
                st.success(f"המוצר '{new_product_name}' נוסף בהצלחה!")
                st.rerun()

    st.markdown("---")
    st.subheader("📁 הוספת קטגוריה חדשה")
    with st.form("add_category_form"):
        new_cat_name = st.text_input("שם הקטגוריה החדשה (עם אימוג'י רצוי):").strip()
        submit_cat = st.form_submit_button(
            "הוסף קטגוריה חדשה", use_container_width=True
        )

        if submit_cat:
            if not new_cat_name:
                st.error("נא להזין שם קטגוריה.")
            elif new_cat_name in catalog:
                st.warning("הקטגוריה כבר קיימת!")
            else:
                catalog[new_cat_name] = []
                save_catalog(catalog)
                st.success(f"הקטגוריה '{new_cat_name}' נוספת בהצלחה!")
                st.rerun()

    st.markdown("---")
    st.subheader("🗑️ מחיקת מוצר מהקטלוג")
    del_cat = st.selectbox("בחר קטגוריה למחיקה ממנה:", list(catalog.keys()), key="del_cat_select")
    if catalog[del_cat]:
        del_item = st.selectbox("בחר מוצר למחיקה:", catalog[del_cat], key="del_item_select")
        if st.button("מחק מוצר זה מהקטלוג", use_container_width=True):
            catalog[del_cat].remove(del_item)
            save_catalog(catalog)
            # הסרה גם מהסל אם הוא קיים שם
            if del_item in st.session_state.cart:
                del st.session_state.cart[del_item]
                save_cart_state(st.session_state.cart)
            st.success(f"המוצר '{del_item}' נמחק בהצלחה.")
            st.rerun()
    else:
        st.info("אין מוצרים בקטגוריה זו.")