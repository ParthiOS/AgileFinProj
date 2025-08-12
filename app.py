
import streamlit as st
import pandas as pd
import numpy as np
from rapidfuzz import process, fuzz
from io import StringIO

st.set_page_config(page_title="Grocery Buddies – Live Demo", page_icon="🛒", layout="wide")

# Expanded embedded CSV data with more cross-store overlap
DATA_CSV = """product_id,name,brand,category,store,price,unit_qty,unit_name,price_per_unit
1,Whole Milk 2%,DairyPure,Dairy,FreshCo,4.19,2,L,2.095
1,Whole Milk 2%,DairyPure,Dairy,No Frills,4.35,2,L,2.175
1,Whole Milk 2%,DairyPure,Dairy,Walmart,4.05,2,L,2.025
1,Whole Milk 2%,Neilson,Dairy,FreshCo,4.39,2,L,2.195
1,Whole Milk 2%,Neilson,Dairy,No Frills,4.49,2,L,2.245
1,Whole Milk 2%,Neilson,Dairy,Walmart,4.29,2,L,2.145
1,Whole Milk 2%,Great Value,Dairy,FreshCo,4.35,2,L,2.175
1,Whole Milk 2%,Great Value,Dairy,No Frills,4.25,2,L,2.125
1,Whole Milk 2%,Great Value,Dairy,Walmart,4.28,2,L,2.14

2,Brown Eggs Large 12ct,Burnbrae,Dairy,FreshCo,3.79,12,ct,0.3158333333
2,Brown Eggs Large 12ct,Burnbrae,Dairy,No Frills,3.49,12,ct,0.2908333333
2,Brown Eggs Large 12ct,Burnbrae,Dairy,Walmart,3.59,12,ct,0.2991666667
2,Brown Eggs Large 12ct,Great Value,Dairy,FreshCo,3.55,12,ct,0.2958333333
2,Brown Eggs Large 12ct,Great Value,Dairy,No Frills,3.44,12,ct,0.2866666667
2,Brown Eggs Large 12ct,Great Value,Dairy,Walmart,3.64,12,ct,0.3033333333

3,Bananas,Dole,Produce,FreshCo,0.79,1,lb,0.79
3,Bananas,Dole,Produce,No Frills,0.74,1,lb,0.74
3,Bananas,Dole,Produce,Walmart,0.77,1,lb,0.77
3,Bananas,Chiquita,Produce,FreshCo,0.72,1,lb,0.72
3,Bananas,Chiquita,Produce,No Frills,0.69,1,lb,0.69
3,Bananas,Chiquita,Produce,Walmart,0.75,1,lb,0.75
3,Bananas,Great Value,Produce,FreshCo,0.73,1,lb,0.73
3,Bananas,Great Value,Produce,No Frills,0.71,1,lb,0.71
3,Bananas,Great Value,Produce,Walmart,0.72,1,lb,0.72

4,Gala Apples,Local,Produce,FreshCo,1.49,1,lb,1.49
4,Gala Apples,Local,Produce,No Frills,1.39,1,lb,1.39
4,Gala Apples,Local,Produce,Walmart,1.45,1,lb,1.45
4,Gala Apples,Great Value,Produce,FreshCo,1.52,1,lb,1.52
4,Gala Apples,Great Value,Produce,No Frills,1.47,1,lb,1.47
4,Gala Apples,Great Value,Produce,Walmart,1.58,1,lb,1.58

5,Basmati Rice 5kg,Tilda,Pantry,FreshCo,12.99,5,kg,2.598
5,Basmati Rice 5kg,Tilda,Pantry,No Frills,13.29,5,kg,2.658
5,Basmati Rice 5kg,Tilda,Pantry,Walmart,12.79,5,kg,2.558
5,Basmati Rice 5kg,India Gate,Pantry,FreshCo,13.35,5,kg,2.67
5,Basmati Rice 5kg,India Gate,Pantry,No Frills,13.49,5,kg,2.698
5,Basmati Rice 5kg,India Gate,Pantry,Walmart,13.09,5,kg,2.618
5,Basmati Rice 5kg,Great Value,Pantry,FreshCo,12.69,5,kg,2.538
5,Basmati Rice 5kg,Great Value,Pantry,No Frills,12.59,5,kg,2.518
5,Basmati Rice 5kg,Great Value,Pantry,Walmart,12.49,5,kg,2.498

6,Olive Oil 1L,Bertolli,Pantry,FreshCo,8.99,1,L,8.99
6,Olive Oil 1L,Bertolli,Pantry,No Frills,9.19,1,L,9.19
6,Olive Oil 1L,Bertolli,Pantry,Walmart,8.79,1,L,8.79
6,Olive Oil 1L,PC,Pantry,FreshCo,9.29,1,L,9.29
6,Olive Oil 1L,PC,Pantry,No Frills,9.49,1,L,9.49
6,Olive Oil 1L,PC,Pantry,Walmart,9.15,1,L,9.15
6,Olive Oil 1L,Great Value,Pantry,FreshCo,8.59,1,L,8.59
6,Olive Oil 1L,Great Value,Pantry,No Frills,8.69,1,L,8.69
6,Olive Oil 1L,Great Value,Pantry,Walmart,8.49,1,L,8.49

7,Chicken Breast Boneless Skinless,Maple Leaf,Meat,FreshCo,5.99,1,lb,5.99
7,Chicken Breast Boneless Skinless,Maple Leaf,Meat,No Frills,6.29,1,lb,6.29
7,Chicken Breast Boneless Skinless,Maple Leaf,Meat,Walmart,5.79,1,lb,5.79
7,Chicken Breast Boneless Skinless,Great Value,Meat,FreshCo,5.89,1,lb,5.89
7,Chicken Breast Boneless Skinless,Great Value,Meat,No Frills,6.09,1,lb,6.09
7,Chicken Breast Boneless Skinless,Great Value,Meat,Walmart,5.79,1,lb,5.79

8,Broccoli Crown,Local,Produce,FreshCo,1.49,1,ct,1.49
8,Broccoli Crown,Local,Produce,No Frills,1.39,1,ct,1.39
8,Broccoli Crown,Local,Produce,Walmart,1.42,1,ct,1.42

9,Greek Yogurt Plain 750g,Oikos,Dairy,FreshCo,4.99,750,g,0.0066533333
9,Greek Yogurt Plain 750g,Oikos,Dairy,No Frills,5.19,750,g,0.00692
9,Greek Yogurt Plain 750g,Oikos,Dairy,Walmart,4.89,750,g,0.00652
9,Greek Yogurt Plain 750g,PC,Dairy,FreshCo,5.39,750,g,0.0071866667
9,Greek Yogurt Plain 750g,PC,Dairy,No Frills,5.49,750,g,0.00732
9,Greek Yogurt Plain 750g,PC,Dairy,Walmart,5.29,750,g,0.0070533333
9,Greek Yogurt Plain 750g,Great Value,Dairy,FreshCo,4.79,750,g,0.0063866667
9,Greek Yogurt Plain 750g,Great Value,Dairy,No Frills,4.89,750,g,0.00652
9,Greek Yogurt Plain 750g,Great Value,Dairy,Walmart,4.69,750,g,0.0062533333

10,Pasta Spaghetti 900g,Barilla,Pantry,FreshCo,1.99,900,g,0.0022111111
10,Pasta Spaghetti 900g,Barilla,Pantry,No Frills,2.09,900,g,0.0023222222
10,Pasta Spaghetti 900g,Barilla,Pantry,Walmart,1.89,900,g,0.0021
10,Pasta Spaghetti 900g,Primo,Pantry,FreshCo,2.09,900,g,0.0023222222
10,Pasta Spaghetti 900g,Primo,Pantry,No Frills,2.19,900,g,0.0024333333
10,Pasta Spaghetti 900g,Primo,Pantry,Walmart,2.05,900,g,0.0022777778
10,Pasta Spaghetti 900g,Great Value,Pantry,FreshCo,1.89,900,g,0.0021
10,Pasta Spaghetti 900g,Great Value,Pantry,No Frills,1.85,900,g,0.0020555556
10,Pasta Spaghetti 900g,Great Value,Pantry,Walmart,1.79,900,g,0.0019888889

11,Tomato Sauce 680ml,Classico,Pantry,FreshCo,1.89,680,ml,0.0027794118
11,Tomato Sauce 680ml,Classico,Pantry,No Frills,1.95,680,ml,0.0028676471
11,Tomato Sauce 680ml,Classico,Pantry,Walmart,1.85,680,ml,0.0027205882
11,Tomato Sauce 680ml,PC,Pantry,FreshCo,1.79,680,ml,0.0026323529
11,Tomato Sauce 680ml,PC,Pantry,No Frills,1.69,680,ml,0.0024852941
11,Tomato Sauce 680ml,PC,Pantry,Walmart,1.74,680,ml,0.0025588235
11,Tomato Sauce 680ml,Great Value,Pantry,FreshCo,1.69,680,ml,0.0024852941
11,Tomato Sauce 680ml,Great Value,Pantry,No Frills,1.64,680,ml,0.0024117647
11,Tomato Sauce 680ml,Great Value,Pantry,Walmart,1.59,680,ml,0.0023382353

12,Cheddar Cheese 400g,Cracker Barrel,Dairy,FreshCo,4.79,400,g,0.011975
12,Cheddar Cheese 400g,Cracker Barrel,Dairy,No Frills,4.99,400,g,0.012475
12,Cheddar Cheese 400g,Cracker Barrel,Dairy,Walmart,4.69,400,g,0.011725
12,Cheddar Cheese 400g,PC,Dairy,FreshCo,4.89,400,g,0.012225
12,Cheddar Cheese 400g,PC,Dairy,No Frills,4.99,400,g,0.012475
12,Cheddar Cheese 400g,PC,Dairy,Walmart,4.79,400,g,0.011975
12,Cheddar Cheese 400g,Great Value,Dairy,FreshCo,4.55,400,g,0.011375
12,Cheddar Cheese 400g,Great Value,Dairy,No Frills,4.59,400,g,0.011475
12,Cheddar Cheese 400g,Great Value,Dairy,Walmart,4.49,400,g,0.011225

13,Brown Bread 675g,Dempster's,Bakery,FreshCo,2.69,675,g,0.0039851852
13,Brown Bread 675g,Dempster's,Bakery,No Frills,2.59,675,g,0.0038370370
13,Brown Bread 675g,Dempster's,Bakery,Walmart,2.58,675,g,0.0038222222
13,Brown Bread 675g,Country Harvest,Bakery,FreshCo,2.55,675,g,0.0037777778
13,Brown Bread 675g,Country Harvest,Bakery,No Frills,2.49,675,g,0.0036888889
13,Brown Bread 675g,Country Harvest,Bakery,Walmart,2.52,675,g,0.0037333333
13,Brown Bread 675g,Great Value,Bakery,FreshCo,2.48,675,g,0.0036740741
13,Brown Bread 675g,Great Value,Bakery,No Frills,2.53,675,g,0.0037481481
13,Brown Bread 675g,Great Value,Bakery,Walmart,2.58,675,g,0.0038222222

14,Tea Bags 100ct,Tetley,Beverages,FreshCo,4.49,100,ct,0.0449
14,Tea Bags 100ct,Tetley,Beverages,No Frills,4.39,100,ct,0.0439
14,Tea Bags 100ct,Tetley,Beverages,Walmart,4.29,100,ct,0.0429
14,Tea Bags 100ct,Red Rose,Beverages,FreshCo,4.35,100,ct,0.0435
14,Tea Bags 100ct,Red Rose,Beverages,No Frills,4.29,100,ct,0.0429
14,Tea Bags 100ct,Red Rose,Beverages,Walmart,4.19,100,ct,0.0419
14,Tea Bags 100ct,Great Value,Beverages,FreshCo,4.05,100,ct,0.0405
14,Tea Bags 100ct,Great Value,Beverages,No Frills,4.09,100,ct,0.0409
14,Tea Bags 100ct,Great Value,Beverages,Walmart,3.99,100,ct,0.0399

15,Butter 454g,Lactantia,Dairy,FreshCo,5.49,454,g,0.012095374
15,Butter 454g,Lactantia,Dairy,No Frills,5.69,454,g,0.012533258
15,Butter 454g,Lactantia,Dairy,Walmart,5.39,454,g,0.011873351
15,Butter 454g,Great Value,Dairy,FreshCo,4.99,454,g,0.010996
15,Butter 454g,Great Value,Dairy,No Frills,5.09,454,g,0.011216
15,Butter 454g,Great Value,Dairy,Walmart,4.89,454,g,0.010779

16,White Sugar 2kg,Redpath,Pantry,FreshCo,2.49,2,kg,1.245
16,White Sugar 2kg,Redpath,Pantry,No Frills,2.59,2,kg,1.295
16,White Sugar 2kg,Redpath,Pantry,Walmart,2.39,2,kg,1.195

17,Ground Coffee 340g,Tim Hortons,Beverages,FreshCo,7.99,340,g,0.0235
17,Ground Coffee 340g,Tim Hortons,Beverages,No Frills,8.19,340,g,0.024088235
17,Ground Coffee 340g,Tim Hortons,Beverages,Walmart,7.79,340,g,0.022911765
17,Ground Coffee 340g,Starbucks,Beverages,FreshCo,9.49,340,g,0.027911765
17,Ground Coffee 340g,Starbucks,Beverages,No Frills,9.69,340,g,0.0285
17,Ground Coffee 340g,Starbucks,Beverages,Walmart,9.29,340,g,0.027323529

18,Breakfast Cereal 500g,Cheerios,Pantry,FreshCo,3.99,500,g,0.00798
18,Breakfast Cereal 500g,Cheerios,Pantry,No Frills,4.19,500,g,0.00838
18,Breakfast Cereal 500g,Cheerios,Pantry,Walmart,3.89,500,g,0.00778
18,Breakfast Cereal 500g,Frosted Flakes,Pantry,FreshCo,4.29,500,g,0.00858
18,Breakfast Cereal 500g,Frosted Flakes,Pantry,No Frills,4.39,500,g,0.00878
18,Breakfast Cereal 500g,Frosted Flakes,Pantry,Walmart,4.19,500,g,0.00838

19,Potato Chips 200g,Lay's,Pantry,FreshCo,2.99,200,g,0.01495
19,Potato Chips 200g,Lay's,Pantry,No Frills,3.19,200,g,0.01595
19,Potato Chips 200g,Lay's,Pantry,Walmart,2.89,200,g,0.01445

20,Canned Tuna 170g,Clover Leaf,Pantry,FreshCo,1.89,170,g,0.011117647
20,Canned Tuna 170g,Clover Leaf,Pantry,No Frills,1.99,170,g,0.011705882
20,Canned Tuna 170g,Clover Leaf,Pantry,Walmart,1.79,170,g,0.010529412

21,Peanut Butter 1kg,Kraft,Pantry,FreshCo,5.99,1,kg,5.99
21,Peanut Butter 1kg,Kraft,Pantry,No Frills,6.19,1,kg,6.19
21,Peanut Butter 1kg,Kraft,Pantry,Walmart,5.79,1,kg,5.79

22,All-Purpose Flour 10kg,Robin Hood,Pantry,FreshCo,13.99,10,kg,1.399
22,All-Purpose Flour 10kg,Robin Hood,Pantry,No Frills,14.49,10,kg,1.449
22,All-Purpose Flour 10kg,Robin Hood,Pantry,Walmart,13.49,10,kg,1.349

23,Bottled Water 24x500ml,Nestle Pure Life,Beverages,FreshCo,3.49,12000,ml,0.0002908333
23,Bottled Water 24x500ml,Nestle Pure Life,Beverages,No Frills,3.59,12000,ml,0.0002991667
23,Bottled Water 24x500ml,Nestle Pure Life,Beverages,Walmart,3.39,12000,ml,0.0002825

24,Toilet Paper 12 Double Rolls,Charmin,Household,FreshCo,9.99,12,ct,0.8325
24,Toilet Paper 12 Double Rolls,Charmin,Household,No Frills,10.49,12,ct,0.8741666667
24,Toilet Paper 12 Double Rolls,Charmin,Household,Walmart,9.79,12,ct,0.8158333333
"""

@st.cache_data
def load_data():
    df = pd.read_csv(StringIO(DATA_CSV))
    # Ensure types are correct
    df["price_per_unit"] = df["price"] / df["unit_qty"]
    return df

def fuzzy_search(df, query, top_n=100, score_cutoff=60):
    if not query:
        return df
    choices = (df["name"] + " " + df["brand"]).tolist()
    results = process.extract(query, choices, scorer=fuzz.WRatio, limit=top_n, score_cutoff=score_cutoff)
    idx = [r[2] for r in results]
    return df.iloc[idx]

def best_deals(df, items):
    summary_rows = []
    for item in items:
        if not item.strip():
            continue
        matches = fuzzy_search(df, item, top_n=500, score_cutoff=60)
        if matches.empty:
            summary_rows.append({"query": item, "product_id": None, "name": "No match", "brand":"", "store": "", "price": np.nan})
            continue
        best_offer = matches.sort_values("price").iloc[0]
        summary_rows.append({
            "query": item,
            "product_id": int(best_offer["product_id"]),
            "name": best_offer["name"],
            "brand": best_offer["brand"],
            "store": best_offer["store"],
            "price": float(best_offer["price"]),
            "unit": f'{best_offer["unit_qty"]} {best_offer["unit_name"]}',
            "price_per_unit": float(best_offer["price_per_unit"]),
        })
    deals_df = pd.DataFrame(summary_rows)
    multi_total = deals_df["price"].sum(min_count=1)
    stores = sorted(df["store"].unique())
    single_store_options = []
    for s in stores:
        cost = 0.0
        coverage = 0
        for item in items:
            if not item.strip():
                continue
            matches = fuzzy_search(df[df["store"]==s], item, top_n=100, score_cutoff=60)
            if matches.empty:
                continue
            cost += float(matches.sort_values("price").iloc[0]["price"])
            coverage += 1
        if coverage>0:
            single_store_options.append({"store": s, "items_covered": coverage, "estimated_total": cost})
    single_df = pd.DataFrame(single_store_options).sort_values(["items_covered","estimated_total"], ascending=[False, True])
    return deals_df, single_df, multi_total

def add_to_cart(cart, row, qty=1):
    key = (row["product_id"], row["store"], row["brand"])
    if key in cart:
        cart[key]["qty"] += qty
    else:
        cart[key] = {
            "product_id": int(row["product_id"]),
            "name": row["name"],
            "brand": row["brand"],
            "store": row["store"],
            "unit": f'{row["unit_qty"]} {row["unit_name"]}',
            "price": float(row["price"]),
            "qty": qty,
        }
    return cart

df = load_data()

with st.sidebar:
    st.header("⚙️ Filters")
    stores = st.multiselect("Filter stores", options=sorted(df["store"].unique()), default=sorted(df["store"].unique()))
    categories = st.multiselect("Filter categories", options=sorted(df["category"].unique()), default=sorted(df["category"].unique()))
    st.caption("Dataset expanded for demo: many brands now appear across multiple stores.")

st.title("🛒 Grocery Buddies – Price Comparison Demo")
search_query = st.text_input("🔎 Search products", placeholder="e.g., milk, bananas, basmati rice...")

work_df = df[df["store"].isin(stores) & df["category"].isin(categories)].copy()
results = fuzzy_search(work_df, search_query, top_n=500, score_cutoff=60) if search_query else work_df.copy()

st.subheader("Compare across stores")
# Toggle to combine brands for comparison
combine_brands = st.checkbox("Combine all brands for comparison", value=False, help="If on, the compare table will include all brands for a given product name.")
if combine_brands:
    group_by_key = ["name","category"]
    label_maker = lambda n,c: f"{n} ({c})"
else:
    group_by_key = ["name","brand","category"]
    label_maker = lambda n,b,c: f"{n} – {b} ({c})"

grouped = results.groupby(group_by_key)
if len(grouped) > 0:
    options = []
    for key in grouped.groups.keys():
        if combine_brands:
            n,c = key
            options.append({"label": label_maker(n,c), "key": key})
        else:
            n,b,c = key
            options.append({"label": label_maker(n,b,c), "key": key})
    selected = st.selectbox("Pick a product to compare:", options=[o["label"] for o in options])
    chosen_key = [o["key"] for o in options if o["label"]==selected][0]

    if combine_brands:
        mask = (results["name"]==chosen_key[0]) & (results["category"]==chosen_key[1])
    else:
        mask = (results["name"]==chosen_key[0]) & (results["brand"]==chosen_key[1]) & (results["category"]==chosen_key[2])

    cmp_df = results[mask].sort_values(["brand","price"]).copy()
    cmp_df = cmp_df[["brand","store","price","unit_qty","unit_name","price_per_unit"]].rename(
        columns={"unit_qty":"qty","unit_name":"unit","price_per_unit":"price/unit"}
    )
    st.dataframe(cmp_df, use_container_width=True)
else:
    st.info("No products to compare with current filters.")

if "cart" not in st.session_state:
    st.session_state.cart = {}

st.subheader("Search results")
if results.empty:
    st.warning("No matches.")
else:
    for i, row in results.sort_values(["name","brand","price"]).iterrows():
        cols = st.columns([4,2,2,2,2])
        with cols[0]:
            st.markdown(f"**{row['name']}**  \n{row['brand']}  \n_{row['category']}_")
            st.caption(f"Store: {row['store']} — Unit: {row['unit_qty']} {row['unit_name']}")
        with cols[1]:
            st.metric("Price", f"${row['price']:.2f}")
        with cols[2]:
            st.metric("Price / Unit", f"${row['price_per_unit']:.4f}")
        with cols[3]:
            qty = st.number_input(f"Qty #{i}", min_value=1, max_value=20, value=1, step=1, label_visibility="collapsed")
        with cols[4]:
            if st.button("Add to Cart", key=f"add_{i}"):
                st.session_state.cart = add_to_cart(st.session_state.cart, row, qty)
                st.success("Added!")

st.subheader("🧺 Basket Optimizer")
items_str = st.text_area("Enter your shopping list (one item per line)", placeholder="milk\nbananas\nolive oil 1L\npasta 900g")
if st.button("Find best deals"):
    items = [x.strip() for x in items_str.splitlines() if x.strip()]
    if not items:
        st.warning("Please enter at least one item.")
    else:
        deals_df, single_df, multi_total = best_deals(work_df, items)
        st.markdown("**Cheapest offers per item (multi-store plan):**")
        st.dataframe(deals_df, use_container_width=True)
        st.write(f"**Multi-store total:** ${multi_total:.2f}")
        if not single_df.empty:
            st.markdown("**Best single-store options:**")
            st.dataframe(single_df, use_container_width=True)
            top = single_df.iloc[0]
            st.info(f"🏆 Suggested: Multi-store = ${multi_total:.2f} vs {top['store']} only = ${top['estimated_total']:.2f}")

st.subheader("🧾 Your Cart")
if not st.session_state.cart:
    st.write("Cart is empty.")
else:
    cart_rows = []
    for (pid, store, brand), item in st.session_state.cart.items():
        cart_rows.append({
            "store": item["store"],
            "name": item["name"],
            "brand": item["brand"],
            "unit": item["unit"],
            "price": item["price"],
            "qty": item["qty"],
            "line_total": item["price"]*item["qty"],
        })
    cart_df = pd.DataFrame(cart_rows)
    cart_total = cart_df["line_total"].sum()
    st.dataframe(cart_df, use_container_width=True)
    st.metric("Cart total", f"${cart_total:.2f}")
    if st.button("Clear cart"):
        st.session_state.cart = {}
        st.success("Cart cleared.")
