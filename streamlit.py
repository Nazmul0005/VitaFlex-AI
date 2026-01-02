import streamlit as st
import requests
import json
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="VitaFlex AI Coach",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "http://localhost:8000/api/v1"

# --- Styles ---
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        color: #155724;
        margin-bottom: 1rem;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        color: #856404;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---

def get_api_status():
    try:
        response = requests.get("http://localhost:8000/")
        return response.status_code == 200
    except:
        return False

# --- Pages ---

def render_home():
    st.title("Welcome to VitaFlex AI 💪")
    st.markdown("""
    Your personal AI-powered health and fitness companion.
    
    ### Features:
    
    *   **🤖 AI Coach**: Chat with your intelligent fitness guide.
    *   **🥗 Food Scanner**: Snap a photo of your meal for instant nutritional analysis.
    *   **📅 Meal Planner**: Get personalized daily meal plans based on your goals.
    *   **🏋️ Workout Planner**: Generate custom workout routines tailored to you.
    """)
    
    st.divider()
    
    if get_api_status():
        st.success("✅ Backend Server is Online")
    else:
        st.error("❌ Backend Server is Offline. Please run `uvicorn com.mhire.app.main:app --reload`")

def render_ai_coach():
    st.header("🤖 AI Health Coach")
    st.caption("Ask me anything about fitness, nutrition, or health!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("How can I help you today?"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/coach",
                        json={"message": prompt}
                    )
                    if response.status_code == 200:
                        ai_response = response.json()["response"]
                        st.markdown(ai_response)
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {e}")

def render_food_scanner():
    st.header("🥗 AI Food Scanner")
    st.caption("Upload a photo of your meal to get nutritional details.")

    uploaded_file = st.file_uploader("Choose a food image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Image", width=540)
            analyze_btn = st.button("🔍 Analyze Food", type="primary")

        if analyze_btn:
            with col2:
                with st.spinner("Analyzing image..."):
                    try:
                        files = {"image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        response = requests.post(f"{BACKEND_URL}/food-scanner", files=files)
                        
                        if response.status_code == 200:
                            result = response.json()
                            if result.get("success"):
                                data = result["analysis"]
                                
                                # Nutrition Facts
                                st.subheader("📊 Nutritional Info")
                                nut_col1, nut_col2, nut_col3, nut_col4 = st.columns(4)
                                nut = data["nutrition"]
                                nut_col1.metric("Calories", f"{nut['calories']}")
                                nut_col2.metric("Protein", f"{nut['protein']}g")
                                nut_col3.metric("Carbs", f"{nut['carbs']}g")
                                nut_col4.metric("Fat", f"{nut['fat']}g")
                                
                                st.divider()
                                
                                # Details
                                st.subheader("📊 Analysis Summary")

                                col1, col2, col3 = st.columns(3)

                                # Column 1: Detected Items
                                with col1:
                                    st.subheader("📝 Detected Items")
                                    for item in data["food_items"]:
                                        st.markdown(f"- {item}")

                                # Column 2: Health Benefits
                                with col2:
                                    st.subheader("✅ Health Benefits")
                                    for item in data["health_benefits"]:
                                        st.markdown(f"- {item}")

                                # Column 3: Concerns (only if exists)
                                with col3:
                                    if data.get("concerns"):
                                        st.subheader("⚠️ Concerns")
                                        for item in data["concerns"]:
                                            st.markdown(f"- {item}")
                                    else:
                                        st.subheader("⚠️ Concerns")
                                        st.markdown("No major concerns detected ✅")
                            else:
                                st.error(f"Analysis failed: {result.get('error')}")
                        else:
                            st.error(f"Server Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

def _render_profile_form(key_prefix="meal"):
    col1, col2 = st.columns(2)
    
    with col1:
        date_of_birth = st.date_input("Date of Birth", value=datetime(1995, 1, 1), key=f"{key_prefix}_dob")
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, key=f"{key_prefix}_weight")
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=175.0, key=f"{key_prefix}_height")
        goal = st.selectbox("Primary Goal", ["Build Muscle", "Lose Weight", "Eat Healthier"], key=f"{key_prefix}_goal")
        
    with col2:
        eating_style = st.selectbox("Diet Type", ["None", "Vegan", "Keto", "Paleo", "Vegetarian", "Balanced"], key=f"{key_prefix}_diet")
        w_type = st.selectbox("Workout Location", ["Gym", "Home"], key=f"{key_prefix}_wtype")
        w_freq = st.slider("Workouts per Week", 1, 7, 3, key=f"{key_prefix}_wfreq")
        
    with st.expander("Detailed Preferences"):
        col3, col4 = st.columns(2)
        with col3:
            is_meat = st.checkbox("Eat Meat?", value=True, key=f"{key_prefix}_meat")
            is_lactose = st.checkbox("Lactose Intolerant?", value=False, key=f"{key_prefix}_lactose")
            caffeine = st.selectbox("Caffeine Intake", ["None", "Occasionally", "Daily"], key=f"{key_prefix}_caffeine")
        with col4:
            sugar = st.selectbox("Sugar Intake", ["None", "Occasionally", "Crave it", "Daily"], key=f"{key_prefix}_sugar")
            allergies = st.text_input("Allergies (comma separated)", key=f"{key_prefix}_allergies")

    return {
        "primary_goal": goal,
        "weight_kg": weight,
        "height_cm": height,
        "is_meat_eater": is_meat,
        "is_lactose_intolerant": is_lactose,
        "allergies": [a.strip() for a in allergies.split(",")] if allergies else [],
        "eating_style": eating_style,
        "caffeine_consumption": caffeine,
        "sugar_consumption": sugar,
        "workout_type": w_type,
        "workout_frequency": w_freq,
        "date_of_birth": date_of_birth.strftime("%Y/%m/%d")
    }

def render_meal_planner():
    st.header("📅 Weekly Meal Planner")
    st.markdown("Generate a customized meal plan based on your dietary preferences and goals.")
    
    profile_data = _render_profile_form("meal")
    
    if st.button("Generate Meal Plan", type="primary"):
        with st.spinner(" Chef AI is cooking up a plan..."):
            try:
                response = requests.post(f"{BACKEND_URL}/meal-planner", json=profile_data)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        plan = result["meal_plan"]
                        
                        tabs = st.tabs(["🍳 Breakfast", "🥗 Lunch", "🍪 Snack", "🍽️ Dinner"])
                        
                        meals = [("breakfast", tabs[0]), ("lunch", tabs[1]), ("snack", tabs[2]), ("dinner", tabs[3])]
                        
                        for meal_key, tab in meals:
                            meal = plan.get(meal_key)
                            with tab:
                                st.subheader(meal["name"])
                                st.info(meal["description"])
                                
                                m_col1, m_col2 = st.columns([1, 1])
                                with m_col1:
                                    st.markdown("#### 📊 Macros")
                                    st.write(f"**Calories:** {meal['calories']}")
                                    st.write(f"**Protein:** {meal['protein']}g")
                                    st.write(f"**Carbs:** {meal['carbs']}g")
                                    st.write(f"**Fat:** {meal['fat']}g")
                                
                                with m_col2:
                                    st.markdown("#### 🗒️ Preparation")
                                    for step in meal["preparation_steps"]:
                                        st.write(f"- {step}")
                                
                                st.markdown("#### 💡 Why this meal?")
                                st.caption(meal["rationale"])
                                
                    else:
                        st.error(f"Failed to generate plan: {result.get('error')}")
                else:
                    st.error(f"Server Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")

def render_workout_planner():
    st.header("🏋️ Personalized Workout Planner")
    st.markdown("Get a workout routine strictly tailored to your body type and environment.")
    
    profile_data = _render_profile_form("workout")
    
    if st.button("Generate Workout", type="primary"):
        with st.spinner("Coach AI is simulating your workout..."):
            try:
                response = requests.post(f"{BACKEND_URL}/workout-planner", json=profile_data)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        workouts = result["workout_plan"]
                        
                        # Just show first day for now as example, or list all
                        for day_workout in workouts:
                            with st.expander(f"📌 {day_workout['day']} - {day_workout['focus']}", expanded=True):
                                
                                # Warmup
                                st.markdown("### 🔥 Warm Up")
                                st.caption(f"_{day_workout['warm_up']['motto']}_")
                                for ex in day_workout['warm_up']['exercises']:
                                    st.markdown(f"**{ex['name']}** | {ex['sets']} sets x {ex['reps']}")
                                    st.text(f"Instructions: {ex['instructions']}")
                                    if ex.get('video_url'):
                                        st.video(ex['video_url'])
                                
                                st.divider()
                                
                                # Main
                                st.markdown("### 💪 Main Routine")
                                st.caption(f"_{day_workout['main_routine']['motto']}_")
                                for ex in day_workout['main_routine']['exercises']:
                                    st.markdown(f"**{ex['name']}** | {ex['sets']} sets x {ex['reps']}")
                                    st.text(f"Rest: {ex['rest']} | Instructions: {ex['instructions']}")
                                    if ex.get('video_url'):
                                        st.video(ex['video_url'])
                                
                                st.divider()
                                
                                # Cooldown
                                st.markdown("### 🧘 Cool Down")
                                st.caption(f"_{day_workout['cool_down']['motto']}_")
                                for ex in day_workout['cool_down']['exercises']:
                                    st.markdown(f"**{ex['name']}** | {ex['sets']} sets x {ex['reps']}")
                                    st.text(f"Instructions: {ex['instructions']}")
                                    if ex.get('video_url'):
                                        st.video(ex['video_url'])
                                    
                    else:
                        st.error(f"Failed: {result.get('error')}")
                else:
                    st.error(f"Server Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- Main App ---

def main():
    with st.sidebar:
        st.title("VitaFlex AI")
        page = st.radio("Navigate", ["Home", "AI Coach", "Food Scanner", "Meal Planner", "Workout Planner"])
        
        st.info("💡 **Tip:** Make sure the FastAPI backend is running on port 8000.")

    if page == "Home":
        render_home()
    elif page == "AI Coach":
        render_ai_coach()
    elif page == "Food Scanner":
        render_food_scanner()
    elif page == "Meal Planner":
        render_meal_planner()
    elif page == "Workout Planner":
        render_workout_planner()

if __name__ == "__main__":
    main()
