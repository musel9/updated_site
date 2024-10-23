import streamlit as st
import pandas as pd
import base64
from datetime import time, datetime
from io import BytesIO
import os

# Authentication dictionary for usernames and passwords
AUTH_USERS = {
    "Muse": "!Muse!",
    "Mohammed": "!Mohammed!",
    "Duha": "!Duha!",
    "Ziyad": "!Ziyad!",
    "Rawan": "!Rawan!",
    "Fahad": "!Fahad!",
}

# List of energy types in Arabic
type_of_energy = ["الطاقة",
    "الطاقة الشمسية", "الطاقة الرياحية", "الطاقة الكهربائية", "الطاقة النووية",
    "الطاقة الحرارية الأرضية", "الطاقة المائية", "الطاقة الكهروضوئية", "الطاقة الحيوية",
    "الطاقة الهيدروجينية", "الطاقة المدية", "الطاقة الحرارية", "الطاقة الكيميائية",
    "الطاقة الشمسية المركزة", "الطاقة المتجددة", "الطاقة غير المتجددة"
]

# Set the direction to RTL for Arabic
st.markdown(
    """
    <style>
    body {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Authentication logic
def login():
    """Simple login form."""
    st.title("تسجيل دخول")

    # Username and password inputs
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        # Check if the username exists and if the password matches
        if username in AUTH_USERS and AUTH_USERS[username] == password:
            st.session_state["logged_in"] = True
            st.success("تم تسجيل الدخول بنجاح!")
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

def logout():
    """Logout function to reset login state."""
    st.session_state["logged_in"] = False
    st.success("تم تسجيل الخروج")

# Load CSV data
def load_data(file_name, columns):
    """Load data from a CSV file if it exists, otherwise return an empty DataFrame."""
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    else:
        return pd.DataFrame(columns=columns)

# Save data to CSV
def save_data(df, file_name):
    """Save the DataFrame to a CSV file."""
    df.to_csv(file_name, index=False)

# Check if user is logged in
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# If not logged in, show the login form
if not st.session_state["logged_in"]:
    login()
else:
    # Show the logout button
    if st.button("تسجيل خروج"):
        logout()

    # Create two tabs: one for Regular News and another for Twitter News
    tabs = st.tabs(["رصد الأخبار", "تواصل إجتماعي"])

    # Helper function for selected time
    def get_selected_time(key_prefix):
        col1, col2 = st.columns(2)
        with col1:
            hour = st.selectbox("الساعة", list(range(1, 25)), index=11, key=f"{key_prefix}_hour")
        with col2:
            minute = st.selectbox("الدقيقة", list(range(0, 60)), index=0, key=f"{key_prefix}_minute")
        return time(hour=hour, minute=minute)

    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

    # File paths for saving data
    NEWS_CSV = "news_data.csv"
    TWITTER_CSV = "twitter_news_data.csv"

    # Regular News Tab
    with tabs[0]:
        # Load data from the CSV if it exists
        st.session_state["news_data"] = load_data(NEWS_CSV, ["التاريخ", "الوقت", "نوع الخبر", "الخبر الرئيسي", "التصنيف", "المقدمة", "الرابط"])

        col_left, col_right = st.columns([2, 1])
        with col_left:
            news_date = st.date_input("التاريخ")
            time_choice = st.selectbox("التوقيت", ["الآن", "اختر"], key="news_time_choice")
            if time_choice == 'الآن':
                current_time = datetime.now()
                news_time = time(hour=current_time.hour, minute=current_time.minute, second=current_time.second)
            else:
                news_time = get_selected_time(key_prefix="news")
            
            st.write(f"الوقت المحدد: {news_time.strftime('%I:%M:%S %p')}")

            news_type = st.selectbox('نوع الخبر', ['خبر', 'مرئي', 'مقال'])
            news_main = st.text_input("الخبر الرئيسي")

        with col_right:
            news_class = st.selectbox('التصنيف', [x for x in type_of_energy])
            news_intro = st.text_area("المقدمة")
            news_url = st.text_area("الرابط")

        submit_button = st.button(label="إرسال الخبر")

        if submit_button:
            new_entry = pd.DataFrame({
                "التاريخ": [news_date],
                "الوقت": [news_time],
                "نوع الخبر": [news_type],
                "الخبر الرئيسي": [news_main],
                "التصنيف": [news_class],
                "المقدمة": [news_intro],
                "الرابط": [news_url]
            })
            st.session_state["news_data"] = pd.concat([st.session_state["news_data"], new_entry], ignore_index=True)
            save_data(st.session_state["news_data"], NEWS_CSV)  # Save to CSV
            st.success("تم إرسال الخبر بنجاح!")

        if not st.session_state["news_data"].empty:
            st.subheader("الأخبار العامة")
            edited_df = st.data_editor(st.session_state["news_data"])
            st.session_state["news_data"] = edited_df
            save_data(edited_df, NEWS_CSV)  # Save edited data to CSV
            st.download_button(
                label="تحميل الأخبار كملف Excel",
                data=to_excel(edited_df),
                file_name="news_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Twitter News Tab
    with tabs[1]:
        st.session_state["twitter_news_data"] = load_data(TWITTER_CSV, ["المنصة", "التاريخ", "الوقت", "المنطقة", "التصنيف", "المحتوى", "التقييم", "الرابط"])

        col_right, col_left = st.columns(2)
        with col_right:
            social_media = st.selectbox('المنصة', ['Twitter X', 'YouTube', 'TikTok', 'Snapchat', 'Instagram', 'facebook', 'Linkedin'])
            social_date = st.date_input("التاريخ", key="social_date")
            social_time_choice = st.selectbox("التوقيت", ["الآن", "اختر"], key="social_time_choice")
            if social_time_choice == 'الآن':
                current_time_2 = datetime.now()
                social_time = time(hour=current_time_2.hour, minute=current_time_2.minute, second=current_time_2.second)
            else:
                social_time = get_selected_time(key_prefix="tweet")
            st.write(f"الوقت المحدد: {social_time.strftime('%I:%M:%S %p')}")  
            social_zone = st.selectbox("المنطقة", ['غير محدد', 'الرياض', 'مكة المكرمة', 'عسير', 'نجران', 'الباحة', 'تبوك', 'القصيم',
                                                    'جازان', 'المنطقة الشرقية', 'الجوف', 'حائل', 'الحدود الشمالية', 'المدينة المنورة'],
                                    key="social_zone")

        with col_left:
            social_content = st.text_area("المحتوى", key="social_content")
            social_class = st.selectbox('التصنيف', ["انقطاع التيار", "شكوى", "فواتير", "مطالبة"], key="social_class")
            social_stage = st.selectbox('التقييم', ["إيجابي", 'سلبي', 'محايد'])
            social_url = st.text_area("الرابط", key="social_url")

        submit_social_button = st.button(label="ارسال")

        if submit_social_button:
            new_tweet_entry = pd.DataFrame({
                "المنصة": [social_media],
                "التاريخ": [social_date],
                "الوقت": [social_time],
                "المنطقة": [social_zone],
                "التصنيف": [social_class],
                "المحتوى": [social_content],
                "التقييم": [social_stage],
                "الرابط": [social_url]
            })
            st.session_state["twitter_news_data"] = pd.concat([st.session_state["twitter_news_data"], new_tweet_entry], ignore_index=True)
            save_data(st.session_state["twitter_news_data"], TWITTER_CSV)  # Save to CSV
            st.success("تم إرسال الخبر الاجتماعي بنجاح!")

        if not st.session_state["twitter_news_data"].empty:
            st.subheader("تحديثات تويتر")
            edited_tweet_df = st.data_editor(st.session_state["twitter_news_data"])
            st.session_state["twitter_news_data"] = edited_tweet_df
            save_data(edited_tweet_df, TWITTER_CSV)  # Save edited data to CSV
            st.download_button(
                label="تحميل بيانات تويتر كملف Excel",
                data=to_excel(edited_tweet_df),
                file_name="twitter_news_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
