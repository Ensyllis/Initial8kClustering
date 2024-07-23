import streamlit as st
import pandas as pd
import re

def load_data():
    return pd.read_csv('Marked_Dataframe.csv')

def highlight_numbers(text):
    # List of months for date detection
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 
              'August', 'September', 'October', 'November', 'December']
    
    # Function to replace numbers with highlighted version if they don't follow specific words or aren't part of a date
    def replace_if_not_special(match):
        number = match.group(0)
        prev_text = match.string[max(0, match.start() - 50):match.start()]
        next_text = match.string[match.end():min(len(match.string), match.end() + 10)]
        
        # Check if the number is part of a date
        for month in months:
            if re.search(rf'{month}\s+\d+,?\s+({number})', prev_text + number + next_text):
                return number  # Don't highlight if it's part of a date

        # Check for special preceding words
        prev_word = prev_text.split()[-1] if prev_text else ''
        if (prev_word.lower() not in ['form', 'rule', 'article', 'item'] 
            and not re.match(r'\d{4}', prev_word) 
            and number not in ['10b5-1'] 
            and not (1900 <= int(number) <= 2017)):
            return f'<span style="background-color: yellow; color: black;">{number}</span>'
        return number

    # Use negative lookbehind to avoid matching numbers after Form, Rule, Article, or a year
    # Also add negative lookahead for specific cases
    pattern = r'(?<!Form\s)(?<!Rule\s)(?<!Article\s)(?<!\d{4}\s)(\d+|10b5-1)(?!\s*,?\s*(?:2007|2008|2009|2010|2011|2012|2013|2014|2015|2016|2017))'
    return re.sub(pattern, replace_if_not_special, str(text))


def main():
    st.set_page_config(layout="wide")  # This will make the page wide
    
    # Load the data
    df = load_data()

    # Get unique categories
    categories = df['Categories'].unique().tolist()

    # Sidebar for category selection
    st.sidebar.title('Navigation')
    category_index = st.sidebar.empty()
    
    # Initialize session state
    if 'current_category_index' not in st.session_state:
        st.session_state.current_category_index = 0

    # Navigation buttons
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        if st.button('◀'):
            st.session_state.current_category_index = (st.session_state.current_category_index - 1) % len(categories)
    with col3:
        if st.button('▶'):
            st.session_state.current_category_index = (st.session_state.current_category_index + 1) % len(categories)

    # Display current category
    current_category = categories[st.session_state.current_category_index]
    category_index.write(f"Category {st.session_state.current_category_index + 1} of {len(categories)}")
    st.sidebar.write(f"Current Category: {current_category}")

    # Filter dataframe based on selected category
    filtered_df = df[df['Categories'] == current_category]

    # Main content area
    st.title('Stock Categories Viewer')
    st.write(f"Showing data for category: {current_category}")
    
    # Display each row as a separate container
    for _, row in filtered_df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 3, 1, 2])
            with col1:
                st.write("**Ticker:**")
                st.write(row['Ticker'])
            with col2:
                st.write("**Description:**")
                st.markdown(highlight_numbers(row['Description']), unsafe_allow_html=True)
            with col3:
                st.write("**Categories:**")
                st.write(row['Categories'])
            with col4:
                st.write("**Reason:**")
                st.write(row['Reason'])
            st.markdown("---")  # Add a horizontal line between entries

if __name__ == "__main__":
    main()