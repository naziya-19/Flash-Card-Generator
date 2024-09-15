import streamlit as st
from Generate_cards import Generate_Flash_Cards  # Adjust the import based on your actual file structure
import pandas as pd
from io import BytesIO

# Define CSS for flip cards with color coding for difficulty
flip_card_css = """
<style>
/* Container for flip cards */
.flip-card {
  background-color: transparent;
  perspective: 1000px;
  margin: 10px;
}

/* The flip card container */
.flip-card-inner {
  position: relative;
  width: 300px;
  height: 200px;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  border-radius: 10px; /* Rounded corners */
}

/* Hide back side of the card */
.flip-card:hover .flip-card-inner {
  transform: rotateY(180deg);
}

/* Front and back sides */
.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  padding: 20px; /* Add padding inside the card */
  box-sizing: border-box; /* Ensure padding does not affect width/height */
}

/* Front side */
.flip-card-front {
  background-color: #f2f2f2;
  color: black;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

/* Back side */
.flip-card-back {
  background-color: #2980b9;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: rotateY(180deg);
}

/* Difficulty color coding */
.difficulty-EASY .flip-card-front {
  background-color: #d4edda; /* Light green for easy */
}

.difficulty-MEDIUM .flip-card-front {
  background-color: #fff3cd; /* Light yellow for medium */
}

.difficulty-HARD .flip-card-front {
  background-color: #f8d7da; /* Light red for hard */
}
</style>
"""

# Streamlit app
st.header("Flash Card Maker")

# Input fields
grade = st.number_input("Enter Grade:", min_value=0, max_value=14, step=1)
subject = st.text_input("Enter Subject:", value="General")
text_to_translate = st.text_area("Text to analyze")

# Button to generate flash cards
if st.button("Generate Flash Cards"):
    if text_to_translate:
        # Generate flash cards
        try:
            flash_cards = Generate_Flash_Cards(context=text_to_translate, subject=subject, grade=grade)
            
            if flash_cards:
                st.markdown(flip_card_css, unsafe_allow_html=True)
                # st.write("Generated Flash Cards:")
                for card in flash_cards:
                    difficulty_class = f"difficulty-{card['difficulty']}"  # Class for difficulty-based color
                    st.markdown(f"""
                    <div class="flip-card {difficulty_class}">
                      <div class="flip-card-inner">
                        <div class="flip-card-front">
                          <h3>Question</h3>
                          <p>{card['question']}</p>
                        </div>
                        <div class="flip-card-back">
                          <h3>Answer</h3>
                          <p>{card['answer']}</p>
                        </div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                # Convert flash cards to DataFrame
                df = pd.DataFrame(flash_cards)

                # Create a BytesIO buffer for the Excel file
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Flash Cards')

                # Create a download button
                buffer.seek(0)
                st.download_button(
                    label="Download Flash Cards as Excel",
                    data=buffer,
                    file_name="flash_cards.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.write("No flash cards generated.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter some text.")
