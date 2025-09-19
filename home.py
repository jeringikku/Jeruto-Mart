import streamlit as st
#import gspread
#from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import requests
from streamlit_lottie import st_lottie
import smtplib
from email.message import EmailMessage

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Load JSON from secrets
#creds_dict = json.loads(st.secrets["general"]["GOOGLE_CREDENTIALS"])

# Load credentials from secrets (already a dict)
creds_dict = st.secrets["service_account"]

# Set scope and authorize
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open your sheet
sheet = client.open("JerutoMartOrders").sheet1


# --- Load Lottie Animation ---
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


# --- Customer Order Animation + Sound ---
def customer_order_feedback():
    st.balloons()  # Balloons animation

    # Optional: Lottie animation
    lottie_animation = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_jcikwtux.json")
    if lottie_animation:
        st_lottie(lottie_animation, height=200)


# --- Owner Notifications (Email + In-app) ---
def owner_order_notification(order_details):
    # In-app notification
    items_text = ", ".join([f"{item['name']} ({item['size']})" for item in order_details["items"]])
    st.success(f"🎉 New Order: {order_details['name']} placed an order!")
    st.info(f"Items: {items_text}\nTotal: ₹{order_details['total']}")



# --- Google Sheets setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#creds = ServiceAccountCredentials.from_json_keyfile_name("servive_account.json", scope)
#client = gspread.authorize(creds)

# Open the sheet by name
sheet = client.open("JerutoMartOrders").sheet1

# --- Page Setup ---
st.set_page_config(page_title="Jeruto Mart", layout="wide")

# --- Custom CSS Styling for Mobile and Desktop ---
st.markdown("""
    <style>
/* --- General Styling --- */
body {
    font-family: 'Arial', sans-serif;
    background-color: #f9f9f9;
}

.ad-image {
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.category-btn {
    background-color: #ff6600;
    color: white;
    padding: 14px 20px;
    border-radius: 12px;
    font-size: 18px;
    margin: 5px 0;
    width: 100%;
    transition: background-color 0.3s ease;
}

.category-btn:hover {
    background-color: #e65c00;
}

.product-card {
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
    background-color: white;
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.product-card:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.offer-price {
    color: red;
    font-weight: bold;
}

.original-price {
    text-decoration: line-through;
    color: gray;
    margin-left: 8px;
}

.cart-section {
    background-color: #fff;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    max-height: 300px;
    overflow-y: auto;  /* Makes cart scrollable on mobile */
}

/* --- Make buttons full width --- */
button {
    width: 100% !important;
    margin-top: 8px;
    padding: 12px 0;
    font-size: 16px;
}

/* --- Mobile Styling --- */
@media (max-width: 768px) {
    h1, h2, h3, h4 {
        font-size: 1.2rem;
    }

    .category-btn {
        font-size: 16px;
        padding: 12px 18px;
        width: 100%;
    }

    .product-card {
        padding: 10px;
        margin: 8px 0;
    }

    .offer-price {
        font-size: 1.1rem;
    }

    .original-price {
        font-size: 0.9rem;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
/* --- Header Styling --- */
.header {
    background-color: #ff6600;
    color: white;
    padding: 20px 0;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
}

/* --- Hero Section Styling --- */
.hero {
    background-image: url('https://via.placeholder.com/1200x300?text=Welcome+to+Jeruto+Mart');
    background-size: cover;
    background-position: center;
    color: white;
    padding: 50px 20px;
    text-align: center;
    border-radius: 12px;
    margin-bottom: 20px;
}
.hero h1 {
    font-size: 36px;
    margin-bottom: 10px;
}
.hero p {
    font-size: 18px;
}

/* --- Footer Styling --- */
.footer {
    background-color: #333;
    color: white;
    text-align: center;
    padding: 20px;
    font-size: 14px;
    border-top: 1px solid #444;
}
</style>
""", unsafe_allow_html=True)

# --- Initialize session state ---
if "current_ad" not in st.session_state:
    st.session_state.current_ad = 0
if "cart" not in st.session_state:
    st.session_state.cart = []

# --- Header Section ---
st.markdown("""
    <div class="header">
        🍯 Jeruto Mart - Authentic Flavors, Delivered Fresh!
    </div>
""", unsafe_allow_html=True)

# --- Logo and Header ---
st.image("assets/logo.jpeg", width=150)
st.title("🍯 Welcome to Jeruto Mart")

# --- Hero Section ---
st.markdown("""
    <div class="hero">
        <h1>Discover Homemade Delights</h1>
        <p>Shop from a wide range of pickles and chutneys made with love and tradition.</p>
    </div>
""", unsafe_allow_html=True)

# --- Scrolling Ads Section ---
st.subheader("🔥 Check out our latest offers!")
ad_images = [
    "https://via.placeholder.com/800x300?text=New+Arrival+Pickles",
    "https://via.placeholder.com/800x300?text=Special+Offers",
    "https://via.placeholder.com/800x300?text=Festive+Discounts"
]
placeholder = st.empty()
prev, next = st.columns([1,1])
with prev:
    if st.button("⬅ Previous"):
        st.session_state.current_ad = (st.session_state.current_ad - 1) % len(ad_images)
with next:
    if st.button("Next ➡"):
        st.session_state.current_ad = (st.session_state.current_ad + 1) % len(ad_images)
placeholder.image(ad_images[st.session_state.current_ad], use_container_width=True, caption="Exciting deals await!")

# --- Category Selection ---
st.subheader("📂 Shop by Category")
categories = ["Pickles", "Chutney Powders"]
selected_category = st.radio("Choose a category:", categories, index=0, horizontal=True)

# --- Product Data ---
products = {
    "Pickles": [
        {
            "name": "Mango Pickle",
            "description": "A traditional, spicy, and tangy mango pickle made from the finest, sun-ripened mangoes. Carefully crafted with hand-picked spices for an authentic homemade taste. Perfect as a side dish with rice, parathas, or snacks to enhance every meal.",
            "image": "assets/Mango.jpeg",
            "sizes": {"100g": 45, "200g": 80, "500g": 200, "1kg": 400},
            "offerPrice": {"100g": 40, "200g": 75,"500g": 185, "1kg": 370}
        },
        {
            "name": "Traditional Fish Pickle",
            "description": "A bold and flavorful fish pickle made with fresh, premium fish and aromatic spices. Slow-cooked to perfection, blending heat, tanginess, and the natural taste of the sea. Pairs wonderfully with plain rice, curd rice, or traditional meals for a burst of flavor. Crafted with care, free from artificial additives, delivering a homemade coastal delight.",
            "image": "assets/Fish.jpeg",
            "sizes": {"100g": 120,"250g": 300, "500g": 600, "1kg": 1200},
            "offerPrice": {"100g": 110,"250g": 275, "500g": 550, "1kg": 1100}
        },
        {
            "name": "Meat Pickle ( Beef )",
            "description": "A rich and hearty beef pickle crafted from premium cuts and aromatic spices. Slow-cooked to bring out deep flavors with the perfect balance of heat and tanginess. Ideal as a side dish with rice, parathas, or festive meals for an unforgettable taste. Prepared traditionally, without artificial preservatives, offering a wholesome and indulgent experience.",
            "image": "assets\Meat.jpeg",
            "sizes": {"100g": 115,"250g": 280, "500g": 560, "1kg": 1120},
            "offerPrice": {"100g": 105,"250g": 260, "500g": 510, "1kg": 1000}
        },
        {
            "name": "Lemon Pickle",
            "description": "A zesty and tangy lemon pickle made from hand-selected fresh lemons and bold spices. low cured to bring out its natural flavors, balancing sourness with a hint of spice. Perfect with rice, snacks, or curries to add a refreshing burst of flavor to every meal. Made with care using natural ingredients, without artificial preservatives, for a wholesome taste.",
            "image": "assets\Lemon.jpeg",
            "sizes": {"250g": 80, "500g": 160, "1kg": 320},
            "offerPrice": {"250g": 70 , "500g": 140, "1kg": 280}
        },
        {
            "name": "Garlic Pickle",
            "description": "A robust and flavorful garlic pickle made with fresh garlic cloves and hand-picked spices. Slow-cooked in mustard oil to enhance its aroma and deliver the perfect balance of heat and tang. A great accompaniment to rice, parathas, and curries, adding a punch of flavor to every bite. Prepared traditionally without artificial additives, offering a healthy, homemade, and bold taste.",
            "image": "assets\Garlic.jpeg",
            "sizes": {"100g": 70,"250g": 175, "500g": 350, "1kg": 700},
            "offerPrice": {"100g": 60,"250g": 160, "500g": 320, "1kg": 640}
        },
        {
            "name": "Lemon Dates Pickle",
            "description": "A unique blend of tangy lemons and naturally sweet dates, crafted with aromatic spices. Slow-cured to create a perfect harmony between sharp citrus and rich, fruity sweetness.  Made with care, using natural ingredients and traditional methods for a wholesome, preservative-free delight.",
            "image": "assets\Lemon_dates.jpeg",
            "sizes": {"100g": 70, "250g": 160, "500g": 320, "1kg": 640},
            "offerPrice": {"100g": 60, "250g": 145, "500g": 275, "1kg": 550}
        },
{
            "name": "Beetroot Pickle",
            "description": "A vibrant and earthy beetroot pickle made from fresh, crisp beetroots and bold spices. Carefully crafted to bring out its natural sweetness with a tangy and mildly spiced twist. Perfect to pair with rice, sandwiches, or snacks for a burst of color and flavor in every meal. Prepared traditionally with natural ingredients, free from artificial preservatives, for a healthy and tasty delight.",
            "image": "assets\Beetroot.jpeg",
            "sizes": {"100g": 60, "250g": 130, "500g": 260, "1kg": 520},
            "offerPrice": {"100g": 50, "250g": 100, "500g": 200, "1kg": 400}
        },

    ],
    "Chutney Powders": [
        {
            "name": "Traditional Coconut Chutney Powder",
            "description": "A fragrant blend of dried coconut, spices, and herbs, crafted for authentic South Indian flavors. Adds a nutty, mildly spicy, and aromatic touch to snacks, dosas, idlis, and rice dishes. Easy to mix with curd or ghee for a quick and delicious accompaniment anytime. Made with natural ingredients, free from artificial preservatives, delivering homemade goodness in every bite.",
            "image": "assets\coconut_chutney.jpeg",
            "sizes": {"50g": 70, "100g": 140, "250g": 340, "500g": 650, "1kg": 1250},
            "offerPrice": {"50g": 60, "100g": 120, "250g": 280, "500g": 550, "1kg": 1100}
        },
        {
            "name": "Mint Chutney",
            "description": "Fresh mint chutney with a hint of lemon.",
            "image": "https://via.placeholder.com/150",
            "sizes": {"100g": 70, "250g": 170, "500g": 280}
        }
    ]
}

# --- Display Products ---
st.subheader(f"🛍️ {selected_category}")

for product in products[selected_category]:
    st.markdown("<div class='product-card'>", unsafe_allow_html=True)
    cols = st.columns([1,3])
    with cols[0]:
        st.image(product['image'], use_container_width=True)
    with cols[1]:
        st.write(f"### {product['name']}")
        st.write(product['description'])

        size = st.selectbox("Select size", options=list(product['sizes'].keys()), key=product['name'])
        original_price = product['sizes'][size]
        offer_price = product.get('offerPrice', {}).get(size, None)

        if offer_price:
            st.markdown(f"<p><span class='offer-price'>₹{offer_price}</span> <span class='original-price'>₹{original_price}</span></p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p><strong>Price: ₹{original_price}</strong></p>", unsafe_allow_html=True)

        if st.button(f"Add {product['name']} ({size}) to Cart", key=product['name'] + size):
            st.session_state.cart.append({
                "name": product['name'],
                "size": size,
                "price": offer_price if offer_price else original_price
            })
            st.success(f"Added {product['name']} ({size}) to cart!")

    st.markdown("</div>", unsafe_allow_html=True)

# --- Cart Section ---
st.markdown("---")
st.subheader("🛒 Your Cart")
st.markdown("<div class='cart-section'>", unsafe_allow_html=True)

if not st.session_state.cart:
    st.info("Your cart is empty.")
else:
    total = 0
    for idx, item in enumerate(st.session_state.cart):
        st.write(f"{item['name']} ({item['size']}) - ₹{item['price']}")
        total += item['price']
    st.markdown(f"### Total: ₹{total}")

    if st.button("Clear Cart"):
        st.session_state.cart = []
        st.success("Cart cleared!")

st.markdown("</div>", unsafe_allow_html=True)

# --- Checkout Form ---
if st.session_state.cart:
    st.markdown("---")
    st.subheader("✅ Checkout")

    with st.form("checkout_form"):
        name = st.text_input("Your Name")
        phone = st.text_input("Mobile Number")
        address = st.text_area("Delivery Address")

        submitted = st.form_submit_button("Place Order")

        if submitted:
            if not name or not phone or not address:
                st.error("Please fill all the fields!")
            else:
                # Prepare order summary
                order_details = {
                    "name": name,
                    "phone": phone,
                    "address": address,
                    "items": st.session_state.cart.copy(),
                    "total": sum(item['price'] for item in st.session_state.cart)
                }

                # Save order to Google Sheets
                try:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    items_text = "\n".join(
                        [f"{item['name']} ({item['size']}) - ₹{item['price']}" for item in order_details["items"]])
                    total_amount = order_details["total"]
                    payment_status = "Pending"  # You can later update this when payment is confirmed

                    # Append the order to the Google Sheet
                    sheet.append_row([
                        timestamp,
                        order_details["name"],
                        order_details["phone"],
                        order_details["address"],
                        items_text,
                        total_amount,
                        payment_status
                    ])
                    st.success("Order placed successfully , Now complete your payment below!")
                    # --- Customer Feedback: Animation + Sound ---
                    customer_order_feedback()

                    # --- Owner Notification: In-app + Email ---
                    owner_order_notification(order_details)



                    # --- Clear cart after placing order ---
                    st.session_state.cart = []

                except Exception as e:
                    st.error(f"Failed to save order: {e}")



                # --- Show order summary ---
                st.write("### Order Summary")
                st.write(f"Name: {order_details['name']}")
                st.write(f"Mobile: {order_details['phone']}")
                st.write(f"Address: {order_details['address']}")
                st.write("Items:")
                for item in order_details["items"]:
                    st.write(f"- {item['name']} ({item['size']}): ₹{item['price']}")
                st.write(f"### Total: ₹{order_details['total']}")

                import qrcode
                from PIL import Image
                import io


                # --- Payment Section ---
                st.markdown("---")
                st.subheader("💳 Pay Now")

                upi_id = "jeringeorgekutty@okaxis"  # Replace with your actual UPI ID
                amount = order_details["total"]
                upi_link = f"upi://pay?pa={upi_id}&pn=JerutoMart&am={amount}&cu=INR"

                st.markdown(f"*UPI ID:* {upi_id}")
                st.markdown(f"*Amount:* ₹{amount}")
                st.markdown("➡ Scan the QR code below or tap the link to pay:")

                # Generate QR Code
                qr = qrcode.make(upi_link)

                qr = qr.resize((150,150))
                buf = io.BytesIO()
                qr.save(buf, format="PNG")
                byte_im = buf.getvalue()

                # Display QR code
                st.image(byte_im, caption="Scan to Pay", use_container_width=False)

                # Also show clickable link
                st.markdown(f"[Or Pay by Clicking here](upi://pay?pa={upi_id}&pn=JerutoMart&am={amount}&cu=INR)")



                # Clear cart after placing order
                st.session_state.cart = []

# --- Footer Section ---
st.markdown("""
    <div class="footer">
        © 2025 Jeruto Mart. All rights reserved.<br>
        Designed for premium homemade flavors.
    </div>
""", unsafe_allow_html=True)